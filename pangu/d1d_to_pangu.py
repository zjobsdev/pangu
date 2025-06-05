# -*- coding: utf-8 -*-
# @Author: wqshen
# @Email: wqshen91@gmail.com
# @Date: 2023/10/8 14:49
# @Last Modified by: wqshen


import os
import sys
import argparse
import numpy as np
import xarray as xr
from logzero import logger, loglevel
from datetime import time, datetime, timedelta
from glob import glob
from bz2 import BZ2File


def infer_inittime():
    now = datetime.utcnow() + timedelta(hours=8)
    now = now.replace(second=0, microsecond=0)
    if now.time() >= time(14, 0):
        return now.replace(hour=0, minute=0)
    elif now.time() >= time(2, 0):
        return now.replace(hour=12, minute=0) - timedelta(days=1)
    else:
        return now.replace(hour=0, minute=0) - timedelta(days=1)


def run(it, input_dir, output_dir='/data/pangu/input/D1D'):
    bzpath_wcard = f'{input_dir}/{it:%Y%m%d/%H}/W_NAFP_C_ECMF_*_P_D1D{it:%m%d%H%M}{it:%m%d%H}011.bz2'
    bzpath = glob(bzpath_wcard)[0]
    with BZ2File(bzpath) as bz2_file:
        last_modified = datetime.fromtimestamp(os.path.getmtime(bzpath))
        filename = os.path.splitext(os.path.basename(bzpath))[0]
        path = os.path.join(output_dir, filename)
        logger.info(f"decompress {os.path.basename(bzpath)} to {path}")
        if os.path.isfile(path) and (datetime.fromtimestamp(os.path.getmtime(path)) >= last_modified):
            logger.info(f"tempfile {bzpath} has existed, skip uncompress.")
        else:
            data = bz2_file.read()
            open(path, "wb").write(data)
            del data

    target_lats = np.linspace(90, -90, 721, dtype='f4')
    target_lons = np.linspace(0, 359.75, 1440, dtype='f4')
    ds_surface = []
    for name in ('msl', '10u', '10v', '2t', '100u', '100v'):
        ds = xr.open_dataset(path, engine='cfgrib', backend_kwargs={'filter_by_keys': {'shortName': name}})
        ds_surface.append(ds)
    ds_surface = xr.merge(ds_surface).interp(latitude=target_lats, longitude=target_lons).astype(np.float32)
    print(ds_surface)

    ds_upper = []
    levels = [1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 50]
    for name in ('gh', 'q', 't', 'u', 'v'):
        ds = xr.open_dataset(path, engine='cfgrib', backend_kwargs={
            'filter_by_keys': {'shortName': name, 'typeOfLevel': 'isobaricInhPa'}}).sel(isobaricInhPa=levels)
        if name == 'gh':
            ds['gh'] = ds['gh'] * 9.80665
            ds = ds.rename({'gh': 'z'})
        ds_upper.append(ds)
    ds_upper = xr.merge(ds_upper).interp(latitude=target_lats, longitude=target_lons).astype(np.float32)
    print(ds_upper)

    ds_d1d = xr.merge([ds_surface, ds_upper])
    os.makedirs(f'{output_dir}/{it:%Y%m%d%H}', exist_ok=True)
    ds_d1d.to_netcdf(f'{output_dir}/{it:%Y%m%d%H}/pangu_input.ecmwf_d1d.{it:%Y%m%d%H}.nc',
                     encoding={v: {'zlib': True, 'complevel': 5} for v in ds_d1d.data_vars})
    # np.save(f"{output_dir}/{it:%Y%m%d%H}/input_surface.npy",
    #         ds_surface.to_array().interp(latitude=target_lats, longitude=target_lons).values.squeeze().astype(np.float32))
    # np.save(f"{output_dir}/{it:%Y%m%d%H}/input_upper.npy",
    #         ds_upper.to_array().interp(latitude=target_lats, longitude=target_lons).values.squeeze().astype(np.float32))


def main_():
    example_text = """Example:
     python d1d_to_pangu.py -r"""

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
                        help='path to d1d field', default='/media/behz/nafp/ECMF-ORIG')
    parser.add_argument('--output-dir', type=str,
                        help='path to output field', default='/data/pangu/input')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    # time check
    if (args.time is not None and args.time.hour not in (0, 12) or
            (args.start is not None and args.start.hour not in (0, 12)) or
            (args.end is not None and args.end.hour not in (0, 12))):
        raise ValueError("hour of time, start and end must be 0 or 12 (UTC) ")

    loglevel(args.loglevel)
    logger.debug(args)

    if args.realtime:
        inittimes = [infer_inittime(), ]
    elif args.start is not None and args.end is not None:
        inittimes = np.arange(args.start, args.end + timedelta(hours=1),
                              np.timedelta64(12, 'h'), dtype='datetime64[h]').astype(datetime)
    else:
        inittimes = [args.time, ]

    for it in inittimes:
        try:
            run(it, args.input_dir, args.output_dir)
            print(it)
        except Exception as e:
            logger.exception(e)
            continue


if __name__ == '__main__':
    main_()
