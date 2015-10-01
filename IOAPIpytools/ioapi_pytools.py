import os
import os.path
import sys
import subprocess
from datetime import datetime


def delete_if_exists(fname):
    """remove a file if it exists, with a message to stdout
    """
    if os.path.exists(fname):
        sys.stdout.write('removed {}\n'.format(fname))
        sys.stdout.flush()
        os.remove(fname)


def ioapi_const_multiply(fname_in,
                         fname_out,
                         in_varname,
                         constant_factor,
                         new_units,
                         new_desc):
    """Multiply a variable in an I/O API file by a constant using M3COMBO
    and place result in a new I/O API file.  Update the file headers
    for the new file with user-specified information.  Models-3 I/O
    API "Logical names" (see Models-3 I/O API documentation) are
    defined internally, allowing the user to specify paths to the
    physical files to be manipulated.

    INPUTS
    fname_in: str; full path to the input Models-3 I/O API file
    fname_out: str; full path to the output Models-3 I/O API file
    in_varname: str; the variable to be multiplied by a constant
    constant_factor: scalar; the constant factor by which to multiply
       in_varname
    new_units: str; units of the variable named in_varname in the output file
    new_desc: str; description text to populate the "desc" field of
       the multiplied variable in the output file

    OUTPUTS
    none

    Author: Timothy W. Hilton, thilton@ucmerced.edu
    """

    os.environ['COMBO_FILES'] = 'infile,'
    os.environ['COMBO_VBLES'] = 'cos,'
    os.environ['COMBO_UNITS'] = '{},'.format(new_units)
    os.environ['cos_VBLES'] = '{},'.format(in_varname)
    os.environ['cos_COEFS'] = '{},'.format(constant_factor)
    os.environ['cos_OFFSET'] = '0.0,'
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

    INPUTS
    fname_griddesc: full path to the GRIDDESC file
    fname_matrix: full path to the binary matrix file to be created
    fname_mattxt: full path to the ASCII matrix file to be created
    in_grid: name of the source grid in the GRIDDESC file
    out_grid: name of the destination grid in the GRIDDESC file
    col_refinement=1000
    row_refinement=1000

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
    """run m3wndw (from the Models-3 I/O API) to window an I/O API file to
    a specified model grid.  Models-3 I/O API "Logical names" (see
    Models-3 I/O API documentation) are defined internally, allowing
    the user to specify paths to the physical files to be
    manipulated.

    INPUTS
    fname_in, fname_out, fname_griddesc, grid_name
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
    """run mtxcple (from the Models-3 I/O API) to regrid a specified
     dataset from a Models-3 I/O API file.  Models-3 I/O API "Logical
     names" (see Models-3 I/O API documentation) are defined
     internally, allowing the user to specify paths to the physical
     files to be manipulated.

    INPUTS
    fname_raw, fname_regridded, fname_matrix, fname_mattxt
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
