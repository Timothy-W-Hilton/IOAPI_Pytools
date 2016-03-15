"""functions useful for regridding Models-3 I/O API data
"""


import os
import os.path
import sys
import subprocess
from datetime import datetime


def delete_if_exists(fname):
    """remove a file if it exists, with a message to stdout

    ARGS:
        fname (string): full path to the file to be removed
    """
    if os.path.exists(fname):
        sys.stdout.write('removed {}\n'.format(fname))
        sys.stdout.flush()
        os.remove(fname)
        if os.path.exists(fname):
            raise OSError('delete_if_exists failed: file still exists')


def ioapi_const_multiply(fname_in,
                         fname_out,
                         in_varname,
                         out_varname,
                         constant_factor,
                         new_units,
                         new_desc):
    """Multiply a variable in a `Models-3 I/O API
    <https://www.cmascenter.org/ioapi/documentation/3.1/html/>`_ file
    by a constant using `M3COMBO
    <https://www.cmascenter.org/ioapi/documentation/3.1/html/M3COMBO.html>`_
    and place result in a new I/O API file.  Update the file headers
    for the new file with user-specified information.  Models-3 I/O
    API `"Logical names"
    <https://www.cmascenter.org/ioapi/documentation/3.1/html/LOGICALS.html>`_
    are defined internally, allowing the user to specify paths to the
    physical files to be manipulated.

    ARGS:
        fname_in (string): full path to the input Models-3 I/O API file
        fname_out (string): full path to the output Models-3 I/O API file
        in_varname (string): the variable to be multiplied by a constant
        out_varname (string): the name of the multiplied variable in
           the output file
        constant_factor (scalar): the constant factor by which to multiply
           in_varname
        new_units (string): units of the variable named in_varname in the
           output file
        new_desc: (string): description text to populate the "desc" field of
           the multiplied variable in the output file

    RETURNS:
        None

    Author: Timothy W. Hilton, thilton@ucmerced.edu

    """

    os.environ['COMBO_FILES'] = 'infile,'
    os.environ['COMBO_VBLES'] = '{},'.format(out_varname)
    os.environ['COMBO_UNITS'] = '{},'.format(new_units)
    os.environ['{}_VBLES'.format(out_varname)] = '{},'.format(in_varname)
    os.environ['{}_COEFS'.format(out_varname)] = '{},'.format(constant_factor)
    os.environ['{}_OFFSET'.format(out_varname)] = '0.0,'
    os.environ['outfile'] = 'OUTPUT_FILE'
    # the logical name of the output file is COMBO_3D -- this differs
    # from m3combo documentation
    os.environ['COMBO_3D'] = fname_out
    os.environ['infile'] = fname_in

    delete_if_exists(fname_out)
    subprocess.call('m3combo << DONE\n'
                    '\n'
                    '\n'
                    '\n'
                    '\n'
                    '\n'
                    '\n'
                    'DONE\n',
                    shell=True)

    #  the m3combo automatically-generated variable description is not
    #  very useful -- replace it with a better one.
    os.environ['INFILE'] = fname_out
    subprocess.call('m3edhdr << DONE\n'
                    '\n'   # accept default infile logical name
                    '5\n'  # option 5: edit variable units, description
                    '\n'   # accept current variable name
                    '\n'   # accept current variable units
                    '{new_desc}\n'  # new vdesc
                    '10\n'  # option 10: quit
                    'DONE\n'.format(new_desc=new_desc),
                    shell=True)


def calculate_regrid_matrix(fname_griddesc, fname_matrix, fname_mattxt,
                            in_grid, out_grid,
                            col_refinement=1000, row_refinement=1000):
    """run mtxcalc (from the Models-3 I/O API) to calculate a regrid
    matrix for a specified grid-to-grid transformation.  Models-3 I/O
    API "Logical names" (see Models-3 I/O API documentation) are
    defined internally, allowing the user to specify paths to the
    physical files to be manipulated.

    ARGS:
        fname_griddesc (string): full path to the GRIDDESC file
        fname_matrix (string): full path to the binary matrix file to
            be created
        fname_mattxt (string): full path to the ASCII matrix file to
            be created
        in_grid (string): name of the source grid in the GRIDDESC file
        out_grid (string): name of the destination grid in the GRIDDESC file
        col_refinement (integer): col_refinement argument to pass to mtxcalc
        row_refinement (integer): row_refinement argument to pass to mtxcalc

    SEE ALSO:
        `Models-3 I/O API mtxcalc documentation
        <https://www.cmascenter.org/ioapi/documentation/3.1/html/MTXCALC.html>`_
    """
    os.environ['GRIDDESC'] = fname_griddesc
    os.environ['MATRIX'] = fname_matrix
    os.environ['MATTXT'] = fname_mattxt
    os.environ['COL_REFINEMENT'] = "{}".format(col_refinement)
    os.environ['ROW_REFINEMENT'] = "{}".format(row_refinement)

    if (os.path.exists(fname_matrix) and os.path.exists(fname_mattxt)):
        sys.stdout.write('{} and {} already exist; '
                         'mtxcalc was not run.\n'.format(
                             fname_matrix, fname_mattxt))
        sys.stdout.flush()
    else:
        sys.stdout.write('calculating regrid matrices')
        sys.stdout.flush()
        t0 = datetime.now()
        cmd = ("mtxcalc << DONE\n"
               "Y\n"
               "{in_grid}\n"
               "{out_grid}"
               "\n"
               "MATTXT\n"
               "DONE\n".format(in_grid=in_grid, out_grid=out_grid))
        subprocess.call(cmd, shell=True)
        sys.stdout.write('done calculating regrid matrices (' +
                         str(datetime.now() - t0) + ")\n")
        sys.stdout.flush()


def window_to_NorthAmerica(fname_in, fname_out, fname_griddesc, grid_name):
    """window SiB I/O API file to one quarter of the globe.

    Uses the Models-3 I/O API utility `m3wndw
    <https://www.cmascenter.org/ioapi/documentation/3.1/html/M3WNDW.html>`_
    to extract data from an I/O API file to a specified subgrid.

    The window_to_NorthAmerica reflects the function's original use to
    extract data that are North of the equator and between 0 W and 180
    W longitude.  Considering this subset (25%) of a global data set
    speeds calculation of regridding matrices considerably.

    Models-3 I/O API `Logical names
    <https://www.cmascenter.org/ioapi/documentation/3.1/html/LOGICALS.html>`_
    are defined internally, allowing the user to specify paths to the
    physical files to be manipulated.

    Args:
        fname_in (string): full path to the global SiB Models-3 I/O
            API file
        fname_out (string): full path for the windowed Models-3
            I/O API file to create.  fname_out is overwritten if it
            exists.
        fname_griddesc (string): full path the Models-3 I/O API
            `GRIDDESC file
            <https://www.cmascenter.org/ioapi/documentation/3.1/html/GRIDDESC.html>`_
            describing the destination grid.
        grid_name (string): the name of the destination grid in the
            GRIDDESC file.

    """

    os.environ['GRIDDESC'] = fname_griddesc
    os.environ['INFILE'] = fname_in
    os.environ['OUTFILE'] = fname_out
    delete_if_exists(fname_out)
    sys.stdout.write('running m3wndw')
    sys.stdout.flush()
    subprocess.call('m3wndw << DONE\n'
                    '\n'
                    '\n'
                    '\n'
                    '\n'
                    '{grid_name}\n'
                    '\n'
                    'DONE'.format(grid_name=grid_name),
                    shell=True)


def run_regrid(fname_raw, fname_regridded, fname_matrix, fname_mattxt):
    """perform mass-conservative regrid of Models-3 I/O API data using
    mtxcple

    run `mtxcple
    <https://www.cmascenter.org/ioapi/documentation/3.1/html/MTXCPLE.html>`_
    (from the `Models-3 I/O API
    <https://www.cmascenter.org/ioapi/documentation/3.1/html/>`_) to
    regrid a specified dataset from a Models-3 I/O API file.

    Models-3 I/O API `Logical names
    <https://www.cmascenter.org/ioapi/documentation/3.1/html/LOGICALS.html>`_
    are defined internally, allowing the user to specify paths to the
    physical files to be manipulated.

    ARGS:
        fname_raw (string): full path for the Models-3 I/O API data
            file containing data on the source grid.
        fname_regridded (string): full path for the regridded Models-3
            I/O API file to create. fname_regridded is overwritten if
            it exists.
        fname_matrix (string): full path for the matrix file (see
            :mod:ioapi_tools.calculate_regrid_matrix)
        fname_mattxt (string): full path for the mattxt file (see
            :mod:ioapi_tools.calculate_regrid_matrix)

    """

    os.environ['IN_DATA'] = fname_raw
    os.environ['OUT_DATA'] = fname_regridded
    os.environ['MATRIX_FILE'] = fname_matrix
    os.environ['FRACTIONS'] = fname_mattxt

    delete_if_exists(fname_regridded)
    subprocess.call('mtxcple << DONE\n'
                    'Y\n'
                    'NONE\n'
                    '\n'
                    '\n'
                    '\n'
                    '\n'
                    '\n'
                    '\n'
                    '\n'
                    '\n'
                    'DONE\n',
                    shell=True)


def run_regrid_NN(fname_raw, fname_regridded, fname_griddesc, out_grid_name):
    """Nearest neighbor regrid using Models-3 I/O API tools.  Run
     m3interp (from the Models-3 I/O API) to regrid a specified
     dataset from a Models-3 I/O API file.  Models-3 I/O API "Logical
     names" (see Models-3 I/O API documentation) are defined
     internally, allowing the user to specify paths to the physical
     files to be manipulated."""

    os.environ['INFILE'] = fname_raw
    os.environ['OUTFILE'] = fname_regridded
    os.environ['GRIDDESC'] = fname_griddesc
    # sys.stdout.write('in run_regrid_NN: ')
    # sys.stdout.flush()
    # delete_if_exists(fname_regridded)
    # sys.stdout.write('\n: ')
    # sys.stdout.flush()
    subprocess.call('m3interp << DONE\n'
                    'Y\n'
                    'NONE\n'
                    '\n'    # accept "INFILE" for input logical name
                    '{}\n'  # output grid name
                    '\n'    # default start date
                    '\n'    # default start time
                    '\n'    # default time step
                    '\n'    # regrid all time steps (default)
                    '\n'    # accept "OUTFILE" for output logical name
                    'DONE\n'.format(out_grid_name),
                    shell=True)


def boundaries_from_csv(fname_csv,
                        fname_bdy,
                        fname_griddesc,
                        gridname,
                        nlevs,
                        file_desc="boundary data"):
    """Create lateral boundary conditions file from data in CSV file

    Run `M3FAKE
    <https://www.cmascenter.org/ioapi/documentation/3.1/html/M3FAKE.html>`_
    to create a boundary condition file from a specified csv file
    containing the boundaries data.  Models-3 I/O API `"Logical names"
    <https://www.cmascenter.org/ioapi/documentation/3.1/html/LOGICALS.html>`_
    are defined internally, allowing the user to specify paths to the
    physical files to be manipulated.

    Currently only `time-independent
    <https://www.cmascenter.org/ioapi/documentation/3.1/html/DATETIME.html>`_
    boundary files are supported.

    Currently can only use the default vertical sigma-P coordinates
    suggested by M3FAKE.

    ARGS:
    fname_csv (string): full path to the comma-separated variable
        data file containing the boundary conditions.
    fname_bdy (string): full path to the Models-3 I/O API boundaries
        file to create.  Will be overwritten if the file already exists.
    fname_griddesc (string): full path to the Models-3 I/O API
       `GRIDDESC
       <http://www.cmascenter.org/ioapi/documentation/3.1/html/GRIDS.html#horiz>`_
       file describing the model grid.
    gridname (string): name of the grid to create boundaries for (must
        be an entry in the GRIDDESC file).
    nlevs (int): number of vertical levels.
    file_desc (string): string to populate the `FDESC3D
        <http://www.cmascenter.org/ioapi/documentation/3.1/html/INCLUDE.html#fdesc>`_
        metadata field in the boundary condition file.  Defaults to
        "boundary data".

    RETURNS:
    None
    """

    os.environ['GRIDDESC'] = fname_griddesc
    os.environ['OUTFILE'] = fname_bdy
    os.environ['CSV_FILE'] = fname_csv

    # some netcdf, I/O API routines barf if the output file exists
    # already -- therefore delete it now
    delete_if_exists(fname_bdy)
    cmd = ('m3fake << DONE\n'
           'Y\n'   #
           '3\n'   # 3 == boundary file
           '{gridname}\n'  # name of grid in GRIDDESC
           '{nlevs}\n'  # number of vertical levels
           '4\n'  # 4 == hydrostatic sigma-P vertical coords
           '\n'  # default sigma-P for model top
           '\n'  # default sigma-P for level 0
           '\n'  # .
           '\n'  # .
           '\n'  # .
           '\n'  # .
           '\n'  # .
           '\n'  # .
           '\n'  # .
           '\n'  # .
           '\n'  # .
           '\n'  # .
           '\n'  # .
           '\n'  # .
           '\n'  # .
           '\n'  # .
           '\n'  # .
           '\n'  # .
           '\n'  # .
           '\n'  # .
           '\n'  # .
           '\n'  # .
           '\n'  # .
           '\n'  # default sigma-P for level 22
           '0\n'  # time-independent file
           '1\n'  # number of variables
           'CO2_TRACER1\n'  # variable name
           'ppbv\n'   # variable units
           '[COS]\n'  # variable description
           '1\n'  # 1 == type real (as opposed to int double etc)
           '1\n'  # 1 == fill file with column number
           #'CSV_FILE\n'  # data file logical name
           '{file_desc}\n\n'
           'OUTFILE\n'  # logical name of boundary file
           'DONE\n'.format(gridname=gridname,
                           nlevs=nlevs,
                           file_desc=file_desc))

    subprocess.call(cmd, shell=True)


def dummy_top_bounds(fname_bdy,
                     fname_griddesc,
                     gridname,
                     file_desc="boundary data"):
    """Create lateral boundary conditions file from data in CSV file

    Run `M3FAKE
    <https://www.cmascenter.org/ioapi/documentation/3.1/html/M3FAKE.html>`_
    to create a top boundary condition file containing 0.0 at all
    locations.  Models-3 I/O API `"Logical names"
    <https://www.cmascenter.org/ioapi/documentation/3.1/html/LOGICALS.html>`_
    are defined internally, allowing the user to specify paths to the
    physical files to be manipulated.

    Currently only `time-independent
    <https://www.cmascenter.org/ioapi/documentation/3.1/html/DATETIME.html>`_
    boundary files are supported.

    ARGS:
    fname_bdy (string): full path to the Models-3 I/O API boundaries
        file to create.  Will be overwritten if the file already exists.
    fname_griddesc (string): full path to the Models-3 I/O API
       `GRIDDESC
       <http://www.cmascenter.org/ioapi/documentation/3.1/html/GRIDS.html#horiz>`_
       file describing the model grid.
    gridname (string): name of the grid to create boundaries for (must
        be an entry in the GRIDDESC file).
    file_desc (string): string to populate the `FDESC3D
        <http://www.cmascenter.org/ioapi/documentation/3.1/html/INCLUDE.html#fdesc>`_
        metadata field in the boundary condition file.  Defaults to
        "boundary data".

    RETURNS:
    None

    """

    os.environ['GRIDDESC'] = fname_griddesc
    os.environ['OUTFILE'] = fname_bdy

    # some netcdf, I/O API routines barf if the output file exists
    # already -- therefore delete it now
    delete_if_exists(fname_bdy)
    cmd = ('m3fake << DONE\n'
           'Y\n'   #
           '2\n'   # 3 == gridded file
           '{gridname}\n'  # name of grid in GRIDDESC
           '1\n'  # number of vertical levels
           '0\n'  # time-independent file
           '1\n'  # number of variables
           'CO2_TRACER1\n'  # variable name
           'ppbv\n'   # variable units
           '[COS]\n'  # variable description
           '1\n'  # 1 == type real (as opposed to int double etc)
           '1\n'  # 1 == fill file with column number
           #'CSV_FILE\n'  # data file logical name
           '{file_desc}\n\n'
           'OUTFILE\n'  # logical name of boundary file
           'DONE\n'.format(gridname=gridname,
                           file_desc=file_desc))

    subprocess.call(cmd, shell=True)


def run_bcwndw(fname_gridded, fname_bdy,
               LOROW=1, HIROW=123,
               LOCOL=1, HICOL=123):
    """Run bcwndw (from the Models-3 I/O API) to create a boundary
    condition file from a specified Models-3 I/O API file containing
    gridded data.  Models-3 I/O API "Logical names" (see Models-3 I/O
    API documentation) are defined internally, allowing the user to
    specify paths to the physical files to be manipulated."""

    os.environ['INFILE'] = fname_gridded
    os.environ['OUTFILE'] = fname_bdy

    delete_if_exists(fname_bdy)
    subprocess.call('bcwndw INFILE OUTFILE << DONE\n'
                    '\n'    # default start date
                    '\n'    # default start time
                    '\n'    # default duration
                    '\n'    # default windowed grid name
                    '\n'    # default for boundary thickness (1)
                    '{LOCOL}\n'
                    '{HICOL}\n'
                    '{LOROW}\n'
                    '{HIROW}\n'
                    'DONE\n'.format(LOCOL=LOCOL, HICOL=HICOL,
                                    LOROW=LOROW, HIROW=HIROW),
                    shell=True)



def concat(file1, file2):
    """concatenate file2 to file1 using m3xtract"""
    os.environ['INFILE'] = file2
    os.environ['OUTFILE'] = file1

    subprocess.call('m3xtract << DONE\n'
                    '\n'  # default logical name for input
                    '0\n'  # all layers
                    '\n'  # all variables
                    '\n'  # default starting date
                    '\n'  # default starting time
                    '\n'  # default duration
                    '\n',  # default logical name for output
                    shell=True)
