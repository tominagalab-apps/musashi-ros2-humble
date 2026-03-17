from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'musashi_basestation'

setup(
    name=package_name,
    version='0.0.0',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # launch files
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        # config files
        ('share/' + package_name + '/config', glob('config/*.rqt')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='todo',
    maintainer_email='todo@todo.todo',
    description='Launch package for musashi basestation GUI components',
    license='TODO',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)