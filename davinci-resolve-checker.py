#!/usr/bin/env python3

import argparse
import distro
import subprocess
import local_strings
from pylspci.parsers import VerboseParser
import pickle
import sys
import os
import json

parser = argparse.ArgumentParser(description="Davinci Resolve checker")
parser.add_argument(
    "-l",
    "--locale",
    help="Locale for messages print by the checker, e.g. 'en_US'",
    dest="locale",
)
parser.add_argument(
    "-p",
    "--pro",
    help="Make checks for AMD proprietary stack (legacy OpenCL and proprietary OpenGL)",
    action="store_true",
    dest="pro_stack",
)
args = parser.parse_args()

local_str = local_strings.LocalStrings(preferred_locale=args.locale)

print(local_str["locale"], local_str.locale)

print(local_str["project name"], "5.2.8")

if distro.id() not in {"arch", "manjaro", "endeavouros", "garuda", "cachyos"}:
    print(
        local_str["you are running"],
        distro.name(),
        "(",
        distro.id(),
        ")",
        local_str["script not tested on distro"],
    )
    exit(1)

dependencies_check = subprocess.run(
    "pacman -Q expac mesa-utils",
    shell=True,
    capture_output=True,
    text=True,
)
if dependencies_check.returncode != 0:
    print(dependencies_check.stderr.strip())
    exit(1)
for module in "pylspci", "distro":
    if module not in sys.modules:
        print("Missing " + module)
        exit(1)

installed_dr_package = subprocess.run(
    "expac -Qs '%n %v' davinci-resolve", shell=True, capture_output=True, text=True
).stdout.rstrip("\n")
print(local_str["which DR package"], installed_dr_package)

chassis_types = {
    # Taken from spec 3.5.0, see here: https://superuser.com/a/1107191/873855
    "1": "Other",
    "2": "Unknown",
    "3": "Desktop",
    "4": "Low Profile Desktop",
    "5": "Pizza Box",
    "6": "Mini Tower",
    "7": "Tower",
    "8": "Portable",
    "9": "Laptop",
    "10": "Notebook",
    "11": "Hand Held",
    "12": "Docking Station",
    "13": "All in One",
    "14": "Sub Notebook",
    "15": "Space-saving",
    "16": "Lunch Box",
    "17": "Main Server Chassis",
    "18": "Expansion Chassis",
    "19": "SubChassis",
    "20": "Bus Expansion Chassis",
    "21": "Peripheral Chassis",
    "22": "RAID Chassis",
    "23": "Rack Mount Chassis",
    "24": "Sealed-case PC",
    "25": "Multi-system chassis",
    "26": "Compact PCI",
    "27": "Advanced TCA",
    "28": "Blade",
    "29": "Blade Enclosure",
    "30": "Tablet",
    "31": "Convertible",
    "32": "Detachable",
    "33": "IoT Gateway",
    "34": "Embedded PC",
    "35": "Mini PC",
    "36": "Stick PC",
}

amd_codenames_pre_vega = ["Ellesmere"]
amd_codenames_vega_and_onward = ["Vega", "Navi", "Cezanne", "Raphael", "Barcelo"]

with open("/sys/class/dmi/id/chassis_type", "r") as file:
    chassis_type = chassis_types[file.read().rstrip()]

installed_opencl_drivers = subprocess.run(
    "expac -Qs '%n %v' opencl-driver", shell=True, capture_output=True, text=True
).stdout.splitlines()
installed_opencl_nvidia_package = subprocess.run(
    "expac -Qs '%n' opencl-nvidia", shell=True, capture_output=True, text=True
).stdout.rstrip("\n")

debugging_with_pickled_lspci = (
    False  # turn to true if want to debug somebody's lspci dump.
)
if not debugging_with_pickled_lspci:
    lspci_devices = VerboseParser().run()
else:
    # Use some dump file. To generate dumps, use dump_lspci_list.py.
    with open(
        "lspci_dumps/optimus_laptop_no_any_driver_for_nvidia.bin", "rb"
    ) as fp:  # Unpickling.
        lspci_devices = pickle.load(fp)

print(local_str["chassis"], local_str.get(chassis_type, chassis_type))
supported_mobile_chassis_types = [
    "Laptop",
    "Notebook",
    "Space-saving",
    "Convertible",
    "Portable",
]
supported_desktop_chassis_types = [
    "Desktop",
    "All in One",
    "Tower",
    "Other",
]  # "Other" is a VM, so treat it as a desktop.
if (
    chassis_type not in supported_desktop_chassis_types
    and chassis_type not in supported_mobile_chassis_types
):
    print(local_str["unsupported chassis"])
    exit(1)
print(local_str["openCL drivers"])
if len(installed_opencl_drivers) == 0:
    print(local_str["not found any opencl-driver"])
else:
    print("\t" + "\n\t".join([str(x) for x in installed_opencl_drivers]))
installed_opencl_drivers = [x.split(" ")[0] for x in installed_opencl_drivers]

# Now we are going to check which GPUs are presented in system.
# According to this link: https://pci-ids.ucw.cz/read/PD/03
# There are four subclasses in PCI 03xx class
# I have seen all of them in machines that I could test, except 0301 - XGA controller
# lspci -d ::0300 - intel gpu or amd primary gpu
# lspci -d ::0302 - nvidia 3d controller on an optimus laptop
# lspci -d ::0380 - amd secondary gpu on an i+a laptop

print(local_str["presented gpus"])
print(
    "\t"
    + "\n\t".join(
        [
            x.device.name
            + " ("
            + local_str["kernel driver"]
            + " "
            + str(x.driver or "-")
            + ")"
            for x in lspci_devices
            if x.cls.id in (0x0300, 0x0301, 0x0302, 0x0380)
        ]
    )
)

GL_VENDOR = subprocess.run(
    'glxinfo | grep "OpenGL vendor string" | cut -f2 -d":"',
    shell=True,
    capture_output=True,
    text=True,
).stdout.strip()
print(local_str["opengl vendor"], GL_VENDOR)
# By GL_VENDOR we can distinguish not only OpenGL Open/Pro implementations, but also a primary GPU in use (kinda).
# See https://stackoverflow.com/questions/19985131/how-identify-the-primary-video-card-on-linux-programmatically for more information.

GL_RENDERER = subprocess.run(
    "glxinfo | grep -i 'OpenGL renderer' | cut -f2 -d ':' | xargs",
    shell=True,
    capture_output=True,
    text=True,
).stdout.strip()
print(
    "OpenGL renderer string: " + GL_RENDERER
)  # Useful when there are several gpus, especially from one vendor
print("clinfo detected platforms and devices:")
found_ready_cl_gpu = False
try:
    clinfo_data = json.loads(
        subprocess.run(
            "clinfo --json", shell=True, capture_output=True, text=True
        ).stdout.strip()
    )
    cl_platform_index = len(clinfo_data["platforms"]) - 1
    while cl_platform_index >= 0:
        number_of_devices = len(clinfo_data["devices"][cl_platform_index]["online"])
        platform_name = clinfo_data["platforms"][cl_platform_index]["CL_PLATFORM_NAME"]
        amd_platform_suffix = ""
        if (
            clinfo_data["platforms"][cl_platform_index]["CL_PLATFORM_ICD_SUFFIX_KHR"]
            == "AMD"
        ):
            # I need to differentiate between orca and roc platforms somehow. They have the same platform name.
            # The only difference I can see (at the moment of opencl-amd 5.4.3-3) is cl_amd_offline_devices in orca's extensions.
            # I guess this check can be invalid for later versions. But now I will use it.
            if (
                "cl_amd_offline_devices"
                in clinfo_data["platforms"][cl_platform_index]["CL_PLATFORM_EXTENSIONS"]
            ):
                amd_platform_suffix = " (orca)"
            else:
                amd_platform_suffix = " (roc)"
        print(
            "\t"
            + platform_name
            + amd_platform_suffix
            + " (number of devices: "
            + str(number_of_devices)
            + ")"
        )

        if platform_name != "Clover" and number_of_devices > 0:
            found_ready_cl_gpu = True

        if (
            clinfo_data["platforms"][cl_platform_index]["CL_PLATFORM_ICD_SUFFIX_KHR"]
            == "AMD"
        ):
            while number_of_devices - 1 >= 0:
                print(
                    "\t\t"
                    + clinfo_data["devices"][cl_platform_index]["online"][
                        number_of_devices - 1
                    ]["CL_DEVICE_BOARD_NAME_AMD"]
                )
                number_of_devices -= 1
        elif (
            clinfo_data["platforms"][cl_platform_index]["CL_PLATFORM_ICD_SUFFIX_KHR"]
            == "MESA"
        ):
            while number_of_devices - 1 >= 0:
                print(
                    "\t\t"
                    + clinfo_data["devices"][cl_platform_index]["online"][
                        number_of_devices - 1
                    ]["CL_DEVICE_NAME"]
                )
                number_of_devices -= 1

        cl_platform_index -= 1
except:
    print("\tWarning: could not parse clinfo data!")

print("")  # Empty line, to separate verdict from configuration info.
if not found_ready_cl_gpu:
    print(
        "Not found opencl platforms with appropriate GPUs. Check that you have installed corresponding driver. Otherwise you cannot run DR."
    )
    # do not exit here, to give a chance to show message when ROC_ENABLE_PRE_VEGA=1 variable needed on AMD.
if GL_VENDOR == "":
    print(local_str["missing opengl vendor"])
    exit(1)

if "opencl-mesa" in installed_opencl_drivers:
    print(local_str["should uninstall opencl-mesa"])
    exit(1)

found_AMD_GPU = None
found_INTEL_GPU = None
found_NVIDIA_GPU = None

for device in lspci_devices:
    if device.cls.id in (0x0300, 0x0301, 0x0302, 0x0380):
        if device.driver == "vfio-pci":
            print(local_str["skipping vfio binded gpu"] % device.device.name)
            continue
        if device.vendor.name == "Intel Corporation":
            if found_INTEL_GPU is None:
                found_INTEL_GPU = device
            else:
                print(local_str["several intel gpus"])
                exit(1)
        if device.vendor.name == "Advanced Micro Devices, Inc. [AMD/ATI]":
            if found_AMD_GPU is None:
                found_AMD_GPU = device
            else:
                print(local_str["several amd gpus"])

                pci_slot = "DRI_PRIME=pci-" + str(device.slot).replace(
                    ":", "_"
                ).replace(
                    ".", "_"
                )  # Example: "DRI_PRIME=pci-0000_02_00_0", see https://docs.mesa3d.org/envvars.html#core-mesa-environment-variables
                gl_renderer_for_gpu = subprocess.run(
                    pci_slot
                    + " glxinfo | grep 'OpenGL renderer' | cut -f2 -d ':' | xargs",
                    shell=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                if GL_RENDERER != gl_renderer_for_gpu:
                    continue  # previous found amd GPU is renderer, and current is not. We keep previous.
                else:
                    found_AMD_GPU = device  # previous found amd GPU is not renderer, so we take this
        if device.vendor.name == "NVIDIA Corporation":
            if found_NVIDIA_GPU is None:
                found_NVIDIA_GPU = device
            else:
                print(local_str["several nvidia gpus"])
                exit(1)

# Updated AMD-NVIDIA Dual GPU Case
if found_AMD_GPU and found_NVIDIA_GPU:
    # Prefer NVIDIA GPU if it's properly set up
    if (
        installed_opencl_nvidia_package
        and found_NVIDIA_GPU.driver == "nvidia"
        and GL_VENDOR == "NVIDIA Corporation"
    ):
        # Ignore AMD GPU and continue with NVIDIA checks
        found_AMD_GPU = None
    else:
        print(local_str["confused by nvidia and amd gpus"])
        exit(1)

if not found_AMD_GPU and not found_NVIDIA_GPU and found_INTEL_GPU:
    print(local_str["only intel gpu, cannot run DR"])
    exit(1)

if found_AMD_GPU:
    if found_INTEL_GPU:
        if chassis_type in supported_mobile_chassis_types:
            print(local_str["mixed intel and amd gpus"])
            exit(1)
        elif GL_VENDOR == "Intel":
            print(local_str["set primary display to PCIE"])
            exit(1)

    if found_AMD_GPU.driver != "amdgpu":
        if found_AMD_GPU.driver == "radeon":
            if (
                "amdgpu" in found_AMD_GPU.kernel_modules
                and "radeon" in found_AMD_GPU.kernel_modules
            ):
                print(local_str["switch from radeon driver to amdgpu"])
                exit(1)
            else:
                print(local_str["no support for amd driver, cannot run DR"])
        print(local_str["not running amdgpu driver, cannot run DR"])
        exit(1)

    is_pre_vega = "Unknown"
    if any(
        codename in found_AMD_GPU.device.name for codename in amd_codenames_pre_vega
    ):
        is_pre_vega = True
    if any(
        codename in found_AMD_GPU.device.name
        for codename in amd_codenames_vega_and_onward
    ):
        is_pre_vega = False
    if is_pre_vega == "Unknown":
        print(local_str["amd codename undetectable"])
        is_pre_vega = True

    if args.pro_stack == True:
        if is_pre_vega == "False":
            print(local_str["pro stack on modern gpu"])

        if GL_VENDOR != "Advanced Micro Devices, Inc.":
            # Note: If you run "progl glmark2", you see there "GL_VENDOR:     ATI Technologies Inc.",
            # but if you run "progl glxinfo", you always get "OpenGL vendor string: Advanced Micro Devices, Inc."
            # independently of you use X or Wayland; I+A, A+I or just AMD gpu in system.
            # So we check if it is "Advanced Micro Devices, Inc.".
            print(local_str["not using Pro OpenGL"])
            exit(1)

        if is_pre_vega == "True":
            if not any(
                appropriate_driver in installed_opencl_drivers
                for appropriate_driver in ["opencl-amd", "opencl-legacy-amdgpu-pro"]
            ):
                print(local_str["missing opencl driver"])
                exit(1)
        else:
            if not any(
                appropriate_driver in installed_opencl_drivers
                for appropriate_driver in ["opencl-amd"]
            ):
                print(local_str["missing opencl driver"])
                exit(1)

        andgpu_pro_libgl_version = (
            subprocess.run(
                "expac -Q '%v' amdgpu-pro-libgl",
                shell=True,
                capture_output=True,
                text=True,
            )
            .stdout.rstrip("\n")
            .partition("_")[0]
        )
        opencl_amd_version = (
            subprocess.run(
                "expac -Q '%v' opencl-amd", shell=True, capture_output=True, text=True
            )
            .stdout.rstrip("\n")
            .partition("-")[0]
        )
        index_of_last_dot = opencl_amd_version.rfind(".")
        opencl_amd_version = opencl_amd_version[:index_of_last_dot]

        if opencl_amd_version != andgpu_pro_libgl_version:
            print(
                local_str["opencl-amd and progl versions mismatch"]
                % (opencl_amd_version, andgpu_pro_libgl_version)
            )
    else:  # do not want pro stack
        # TODO Test if DR can actually work when one GPU is renderer and another is cl.
        # Currently 18.1.4-1 it crashes when I run as OCL_ICD_VENDORS=/home/me/ocl/roc-only/ davinci-resolve when there are two AMD and primary is pre-vega.
        if is_pre_vega:
            if os.environ.get("ROC_ENABLE_PRE_VEGA", "0") != "1":
                print(local_str["use roc_enable_pre_vega or use pro stack"])
                exit(1)

        if not any(
            appropriate_driver in installed_opencl_drivers
            for appropriate_driver in ["rocm-opencl-runtime", "opencl-amd"]
        ):
            print(local_str["missing opencl-driver for amd"])
            exit(1)
        elif "opencl-amd" in installed_opencl_drivers:
            print(local_str["use rocm only instead of opencl-amd"])
            exit(1)
        elif "rocm-opencl-runtime" in installed_opencl_drivers:
            print(local_str["good to run DR"])

if found_NVIDIA_GPU:
    # I have tested it with DR 16.2.3 and found out that BMD have fixed that issue. See https://www.youtube.com/watch?v=NdOGFBHEnkU
    # So I will keep this comment for a while, then will remove it.
    # if 'opencl-amdgpu-pro-orca' in installed_opencl_drivers or 'opencl-amdgpu-pro-pal' in installed_opencl_drivers or 'opencl-amd' in installed_opencl_drivers:
    #     print("You have installed opencl for amd, but DaVinci Resolve stupidly crashes if it is presented with nvidia gpu. Remove it, otherwise you could not use DaVinci Resolve.")
    if not installed_opencl_nvidia_package:
        print(local_str["missing opencl-nvidia package"])
        exit(1)
    if found_NVIDIA_GPU.driver != "nvidia":
        print(local_str["missing nvidia as kernel driver"])
        exit(1)
    if GL_VENDOR != "NVIDIA Corporation":
        print(local_str["not running nvidia rendered"])
        exit(1)
    print(local_str["good to run DR"])
