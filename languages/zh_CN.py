local_str = {
    "locale": "使用语言环境:",
    "project name": "达芬奇调色检测工具",
    "you are running": "您使用的是",
    "script not tested on distro": "发行版本，但是本脚本尚未在该发行版上进行测试.",
    "which DR package": "已安装达芬奇调试:",
    "chassis": "设备类型:",
    "openCL drivers": "已安装的OpenCL驱动:",
    "presented gpus": "显卡型号:",
    "kernel driver": "内核驱动:",
    "opengl vendor": "OpenGL供应商:",
    "missing opengl vendor": "无法查询OpenGL供应商信息。您的显卡型号可能是Intel，然而您在尝试使用AMD Pro OpenGL或您在SSH环境下运行本程序。",
    "should uninstall opencl-mesa": "您需要卸载opencl-mesa，否则达芬奇(v17.1.1)将无法运行: 镜像已损坏。但是如果您在设置中反选gpu复选框然后重新启动达芬奇，那么可能会导致整个桌面会话都会损坏，您只能重新启动您的电脑。 至少在AMD显卡上可以观察到这一点。",
    "several intel gpus": "检测到您有多个INTEL显卡。您是否在使用多CPU台式机主板？还是intel igpu + intel dgpu（在编写本程序的时候尚未发现这一现象）？",
    "several amd gpus": "检测到您有多个AMD显卡。您准备使用哪一个？",
    "several nvidia gpus": "检测到您有多个NVIDIA显卡。您准备使用哪一个？",
    "confused by nvidia and amd gpus": "检测到您有AMD和NVIDIA显卡。您准备使用哪一个？",
    "amd gpu binded to vfio-pci": "您的AMD显卡已绑定到 vfio-pci，将不再进行进一步检查。",
    "nvidia gpu binded to vfio-pci": "您的NVIDIA显卡已绑定到 vfio-pci，将不再进行进一步检查。",
    "only intel gpu, cannot run DR": "您只有英特尔显卡。目前达芬奇无法将英特尔显卡用于OpenCL。因此您不能运行达芬奇。详情请参考https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=81579",
    "mixed intel and amd gpus": "暂未找到适用于英特尔+AMD显卡的笔记本电脑的工作配置。您是不是使用的这个型号的笔记本？",
    "set primary display to PCIE": "检测到您的主显卡是英特尔。您可以在UEFI设置中将主显示器设置为PCIE。否则您将无法使用DaVinci Resolve（尚未测试）。",
    "switch from radeon driver to amdgpu": "您当前正在使用RADEON驱动程序。请参照ArchWiki将驱动程序切换到amdgpu：https://wiki.archlinux.org/title/AMDGPU#Enable_Southern_Islands_(SI)_and_Sea_Islands_(CIK)_support。否则您将无法运行达芬奇。",
    "no support for amd driver, cannot run DR": "您的GPU仅支持radeon驱动程序。达芬奇需要使用amdgpu progl才能运行，因为它只能与amdgpu驱动一起使用。因此，您无法运行达芬奇。",
    "not running amdgpu driver, cannot run DR": "出于某种原因，您没有运行amdgpu驱动程序。 您无法运行达芬奇。",
    "not using Pro OpenGL": "您没有使用Pro OpenGL。请安装amdgpu-pro-libgl并在运行达芬奇的时候使用progl前缀运行。否则程序可能会闪退或无法运行。",
    "missing opencl driver": "您的计算机没有用于AMD显卡的opencl驱动程序。请安装该驱动程序，否则您无法使用达芬奇。",
    "good to run DR": "恭喜您，您可以正常使用达芬奇了！",
    "missing opencl-nvidia package": "您没有opencl-nvidia包（或提供opencl-nvidia的替代包）。请务必安装它，否则您将无法使用达芬奇。即使您打算使用cuda，opencl-nvidia也是其必需的依赖项。",
    "missing nvidia as kernel driver": "您没有使用nvidia作为内核驱动程序。请使用专有的nvidia驱动程序，否则您将无法使用达芬奇。",
    "not running nvidia rendered": "您没有运行NVIDIA渲染器。尝试使用prime-run或其他optimus方法运行脚本，否则无法确保您可以正常使用使用达芬奇。",
}
