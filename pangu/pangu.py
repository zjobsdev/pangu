# -*- coding: utf-8 -*-
# @Author: wqshen
# @Email: wqshen91@gmail.com
# @Date: 2023/10/8 9:11
# @Last Modified by: wqshen


import os
import sys
import onnx
import logzero
import argparse
import numpy as np
import xarray as xr
import onnxruntime as ort
from logzero import logger
from datetime import time, datetime, timedelta
from timer import Timer


def infer_inittime():
    now = datetime.utcnow() + timedelta(hours=8)
    now = now.replace(second=0, microsecond=0)
    if now.time() >= time(14, 0):
        return now.replace(hour=0, minute=0)
    elif now.time() >= time(2, 0):
        return now.replace(hour=12, minute=0) - timedelta(days=1)
    else:
        return now.replace(hour=0, minute=0) - timedelta(days=1)


@Timer(name='load_model_session', logger=logger.info)
def load_model_session(hour_step=3, path='./'):
    path_model = f'{path}/pangu_weather_{hour_step}.onnx'
    logger.info(f"load {path_model} and start session")
    model = onnx.load(path_model)
    options = ort.SessionOptions()
    options.enable_cpu_mem_arena = False
    options.enable_mem_pattern = False
    options.enable_mem_reuse = False
    # Increase the number for faster inference and more memory consumption
    options.intra_op_num_threads = 1
    # Set the behavier of cuda provider
    cuda_provider_options = {'arena_extend_strategy': 'kSameAsRequested', }
    ort_session = ort.InferenceSession(path_model, sess_options=options,
                                       providers=[('CUDAExecutionProvider', cuda_provider_options)])
    return model, ort_session


@Timer(name='write_netcdf4', logger=logger.info)
def write(inittime, fh, output, output_surface, output_dir):
    lats = np.linspace(90, -90, 721)
    lons = np.linspace(0, 359.75, 1440)
    level = np.array([1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 50])
    attrs = {'gh': {'long_name': 'Geopotential height', 'units': 'gpm'},
             'q': {'long_name': 'Specific humidity', 'units': 'kg kg**-1'},
             't': {'long_name': 'Temperature', 'units': 'K'},
             'u': {'long_name': 'U component of wind', 'units': 'm s**-1'},
             'v': {'long_name': 'V component of wind', 'units': 'm s**-1'},
             'msl': {'long_name': 'Mean sea level pressure', 'units': 'Pa'},
             'u10': {'long_name': '10 metre U wind component', 'units': 'm s**-1'},
             'v10': {'long_name': '10 metre V wind component', 'units': 'm s**-1m s**-1'},
             't2m': {'long_name': '2 metre temperature', 'units': 'K'},
             }
    z, q, t, u, v = output
    mslp, u10, v10, t2m = output_surface
    time = inittime + timedelta(hours=fh)
    ds = []
    encoding = {'zlib': True, 'complevel': 1}
    for d, name in zip((z, q, t, u, v, mslp, u10, v10, t2m), ('z', 'q', 't', 'u', 'v', 'msl', 'u10', 'v10', 't2m')):
        dims = ('time', 'level', 'lat', 'lon') if d.ndim == 3 else ('time', 'lat', 'lon')
        coords = {'time': [time], 'level': level, 'lat': lats, 'lon': lons} \
            if d.ndim == 3 else {'time': [time], 'lat': lats, 'lon': lons}
        if name == 'z':
            name = 'gh'
            d = d / 9.80665
            attr = attrs['gh']
        else:
            attr = attrs[name]

        dar = xr.DataArray(d[None, ...], dims=dims, coords=coords, name=name, attrs=attr)
        ds.append(dar)
    ds = xr.merge(ds)
    for v in ('level', 'lat', 'lon'):
        coords_attrs = {'level': {'long_name': 'pressure', 'units': 'hPa'},
                        'lat': {'long_name': 'latitude', 'units': 'degrees_north'},
                        'lon': {'long_name': 'longitude', 'units': 'degrees_east'}}
        for m, n in coords_attrs[v].items():
            ds[v].attrs[m] = n

    encoding = {v: encoding for v in ds.data_vars}
    os.makedirs(f'{output_dir}/{inittime:%Y%m%d%H}', exist_ok=True)
    # TODO: compress consume too much time, 0.2s -> 5-7s
    ds.to_netcdf(f'{output_dir}/{inittime:%Y%m%d%H/pangu.I%Y%m%d%H}.{fh:03d}.F{time:%Y%m%d%H}.nc') #, encoding=encoding)


@Timer(name='load_pangu_input', logger=logger.info)
def load_input(inittime, fh, hour_step, input_dir, output_dir):
    def prepare_input(path):
        ds = xr.open_dataset(path)
        if 'z' not in ds and 'gh' in ds:
            ds['z'] = ds['gh'] * 9.80665
        input = ds[upper_vars].to_array().squeeze().values.astype('f4')
        input_surface = ds[surf_vars].to_array().squeeze().values.astype('f4')
        return input, input_surface

    surf_vars = ['msl', 'u10', 'v10', 't2m']
    upper_vars = ['z', 'q', 't', 'u', 'v']
    input, input_surface = None, None
    if fh == hour_step:
        p = f'{input_dir}/{inittime:%Y%m%d%H}/pangu_input.ecmwf_d1d.{inittime:%Y%m%d%H}.nc'
        logger.info(f"{inittime:%Y%m%d%H}-{fh:03d}-{p}")
        input, input_surface = prepare_input(p)
    else:
        step_list = (24, 6, 3, 1)
        for step in step_list:
            if fh % step == hour_step:
                input_fh = fh - hour_step
                ld = inittime + timedelta(hours=input_fh)
                p = f'{output_dir}/{inittime:%Y%m%d%H/pangu.I%Y%m%d%H}.{input_fh:03d}.F{ld:%Y%m%d%H}.nc'
                logger.info(f"{inittime:%Y%m%d%H}-{input_fh:03d}-{p}")
                input, input_surface = prepare_input(p)
                break
    return input, input_surface


def run_model(inittime, input_dir, output_dir, model_path):
    step_list = (24, 6, 3, 1)
    for i, hourstep in enumerate(step_list):
        model, session = load_model_session(hourstep, model_path)
        for fh in range(hourstep, 360 + 1, hourstep):
            if any([fh % pre == 0 for pre in step_list[:i]]):
                continue
            if hourstep == 1 and fh > 84:
                continue
            logger.info(f"processing at inittime={inittime:%Y%m%d%H}, fh={fh:03d}")
            input, input_surface = load_input(inittime, fh, hourstep, input_dir, output_dir)
            if input is None and input_surface is None:
                logger.info("using previous output as input.")
                input, input_surface = input_pre, input_surface_pre
            with Timer(name='pangu_inference', logger=logger.info):
                output, output_surface = session.run(None, {'input': input, 'input_surface': input_surface})
            write(inittime, fh, output, output_surface, output_dir)
            input_pre, input_surface_pre = output, output_surface
        del model, session, input, input_surface, output, output_surface, input_pre, input_surface_pre


def run():
    example_text = """Example:
     python pangu -r"""

    package_root = os.path.abspath(os.path.dirname(__file__))

    def time_parser(s):
        return datetime.strptime(s, '%Y%m%d%H')

    parser = argparse.ArgumentParser(description='Forecast',
                                     epilog=example_text,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-r', '--realtime', action='store_true',
                        help='realtime run', )
    parser.add_argument('-t', '--time', type=time_parser,
                        help='model initial time (UTC) or obs time (BJT)', )
    parser.add_argument('-p', '--start', type=time_parser,
                        help='start time (UTC, except tp01 BJT)', default=None)
    parser.add_argument('-q', '--end', type=time_parser,
                        help='end time (UTC, except tp01 BJT', default=None)
    parser.add_argument('-o', '--loglevel', type=int,
                        help='loglevel: 10, 20, 30, 40, 50', default=20)
    parser.add_argument('--input-dir', type=str,
                        help='path to input field', default='/data/pangu/input')
    parser.add_argument('--output-dir', type=str,
                        help='path to output field', default='/data/pangu')
    parser.add_argument('--model-path', type=str,
                        help='path to pretrained model', default='./')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    # time check
    if (args.time is not None and args.time.hour not in (0, 12) or
            (args.start is not None and args.start.hour not in (0, 12)) or
            (args.end is not None and args.end.hour not in (0, 12))):
        raise ValueError("hour of time, start and end must be 0 or 12 (UTC) ")

    logzero.loglevel(args.loglevel)
    logger.debug(args)

    if args.realtime:
        inittimes = [infer_inittime(), ]
    elif args.start is not None and args.end is not None:
        inittimes = np.arange(args.start, args.end + timedelta(hours=1),
                              np.timedelta64(12, 'h'), freq='datetime64[h]')
    else:
        inittimes = [args.time, ]

    for it in inittimes:
        run_model(it, args.input_dir, args.output_dir, args.model_path)


if __name__ == '__main__':
    run()
