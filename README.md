# Vision MSI Thermal Control

MSI Modern 15H AI C1MG-096IT Linux thermal management - Reverse engineered EC control with fan profiles and battery threshold

## 🎯 Purpose of this Project

This application was born out of necessity for MSI laptop users on Linux. The journey began when I discovered that neither Intel nor MSI provided proper drivers or control applications for my Linux Mint Xia distribution.

## 📖 The Backstory

After extensive searching, only one repository showed promise for my Intel Core Ultra 5 125H CPU:
**[OpenFreezeCenter](https://github.com/YoCodingMonster/OpenFreezeCenter)**

However, this project was originally designed for Intel 10th/12th gen CPUs. My Meteor Lake architecture with P-cores and E-cores presented unique challenges that the original software couldn't fully comprehend.

## 🔧 The Solution

I embarked on a year-long reverse engineering journey to:
- Decode the MSI Embedded Controller (EC) protocol
- Map temperature sensors and fan control registers  
- Implement proper battery charge threshold management
- Create a reliable background daemon for continuous operation

## 🛠️ Development Notes

This project was developed following modern development practices where AI tools assist with code implementation, while all architectural decisions, reverse engineering, and problem solving remain human-driven.

### Human Work:
- **Reverse Engineering**: Embedded Controller address mapping and protocol analysis
- **System Architecture**: Daemon design, GUI structure, and system integration
- **Problem Solving**: Identifying thermal issues and designing solutions
- **Testing & Validation**: Months of manual testing and temperature monitoring
- **Documentation**: Technical specifications and user guides

### AI-Assisted Work:
- Code implementation and syntax assistance
- Debugging support and error resolution
- Documentation formatting and structure

### Credit Distribution:
- **Reverse Engineering & Architecture**: 100% human work
- **Problem Identification & Solution Design**: 100% human work  
- **EC Address Mapping**: 100% human work (0x68, 0x80, 0xbf, etc.)
- **Code Implementation**: AI-assisted development
- **Testing & Validation**: 100% human work

> *"The AI didn't know my EC addresses were 0x68 for CPU temp and 0xbf for battery - I discovered those through extensive reverse engineering and testing!"*

This approach mirrors how professional developers use tools like GitHub Copilot today - as assistants that implement solutions for human-identified problems.

## 📊 Results Achieved

- **Temperature Improvement**: Reduced idle temperatures from 80°C+ to **55°-65°C range**
- **Background Operation**: Full systemd service integration
- **Battery Protection**: Configurable charge limits (50-100%)
- **Multiple Fan Profiles**: Auto, Basic, Advanced, and Cooler Booster modes

## 🖥️ GUI Interface

While not the most visually stunning application, it provides practical control over:
- Real-time temperature monitoring
- Fan profile selection
- Battery threshold configuration
- System status display

## ⚙️ Technical Notes

- **Kernel Limitation**: Linux kernel 6.8.8 lacks complete support for Intel hybrid architectures
- **CPU Governor**: Requires `cpufrequtils` with performance governor for optimal operation
- **Inspiration**: Based on functionality from MSI's "MSI Center" Windows application

## 💡 For Other MSI Users

This project is specifically tuned for MSI Modern 15H AI C1MGT-096IT.  
If you have a different MSI model, the EC addresses will likely need adjustment.

The core architecture should work - you'll just need to map your specific hardware addresses.

## FYI: Why This Project Exists

This project was created because my laptop (**MSI Modern 15H AI C1MG-096IT**) is not supported by **msi_ec** or **MControlCenter**:

- **msi_ec**: Attempting to load it resulted in: `modprobe: ERROR: could not insert 'msi_ec': Operation not supported`
Current compatibility status: *Unimplemented*.

- **MControlCenter**: Running the app always gave:  
[Reddit post about the issue](https://www.reddit.com/r/Ubuntu/comments/1j9frq5/failed_to_load_ec_sys_kernel_module/)

I developed this program to manage and control my system because existing tools didn’t work.  
If you have a supported laptop, I recommend using **msi_ec** or **MControlCenter**.  
This project serves as a fallback for unsupported hardware.

---

## 🔧 For Developers

The project structure is designed to be adaptable. While I can't provide active support for other models, the code is well-documented for those who want to attempt EC reverse engineering on their own hardware.

---

**After spending a year on this project** - through countless nights of reverse engineering, temperature testing, and debugging - I'm finally proud to share this solution with the community. 

What started as sheer frustration with my laptop's thermal performance has evolved into a functional tool that actually works. 


If you have a different MSI model, the architecture is there - you might just need to modify a few EC addresses. The hard part (understanding how MSI's EC works) is already done.

*From one frustrated MSI Linux user to another - I hope this helps you as much as it helped me.*

---

## License Notice

This project includes installation or helper files originally derived from
OpenFreezeCenter, which is licensed under AGPL-3.0.  
To maintain license compatibility, this project is distributed under the
**GNU AGPL-3.0 License**.

All new code (reverse engineering, battery mappings, EC tools, etc.) is
original work by Anthonippillai Vincent Nishan.

