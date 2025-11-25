# Vision MSI Thermal Control

MSI Modern 15H AI C1MGT-096IT Linux thermal management - Reverse engineered EC control with fan profiles and battery threshold

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

## 🚀 Installation

The project includes an installer script for easy deployment on compatible systems.

---

*After a year of testing, debugging, and countless revisions, I'm proud to share this solution with the community. What started as personal frustration has evolved into a functional tool that might help other MSI Linux users facing similar challenges. And i hope that if someone needs it, even having other cpu, they could just modify few numbers*
