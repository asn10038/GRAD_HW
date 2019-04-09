# Homework 3 Report
---
### Damballa RN DGA's Case Study Summary
The case study covers Malware that use Domain Generation algorithms to bypass domain blacklists. Attackers change the domains associated with the command and control servers so that AV can't block the requests. The particular malware that was uncovered in this case study was a Zeus v3 variant that used Peer to Peer as its primary command-and-control mechanism but used DGA domains if it failed.

Damballa began tracking down the malware by monitoriing nonexistent domain name responses (NXDomains).  After a list of fake domains was compiled they were clustered and mapped back to the registered domains used by the attackers. Damballa continued to work backwards to find exploit sites, redirector domains, and the original spam messages. 

After clustering they tagged the clusters as either *Known Malicious* or *Unknown*. DGA's generate thousands of domains per week so tackling the problem at this scale is untenable by human users. 

After clustering, to track the original C&C server Damballa associated the many domain names with only a few ip addresses. An email address is associated with all domain names so they looked up the associated email address and found a few domains associated with the email address. Once the questionable sites were tracked down it was easy to get a copy of the malware for analysis and verify that the domains caught by the clustering algorithm were indeed related to this particular malware. Checking the malicious distribution domains Damballa found this malware was spread via Better Business Bureau and NACHA spamming campaigns.

The malware was an executable meant for a Windows 7 64 bit environment, and was downloaded into ...\AppData\Roaming. By putting it in this folder it meant that on an enterprise system this executable would remain available regardless of the machine every time the user logged in. The malware also created firewall rules, and autostart registry entries so that the malware could function correctly. To avoid AV the malware is polymorphic, meaning that the actualy contents vary but the function remains the same. The intent of the malware is to steal banking information and then exfiltrate that info via encrypted HTTP POST requests. The first attempt to connect to the botnet and the criminal operator is to use P2P connections. If none are available it resorts to  domain generation. The malware uses the data as the seed for the random domains.


### Symantec 2019 1Q threat report
* Overall ransomware was down 20%
* Mobile ransomware was up 33%
* Malicious powershell scripts were up 100%
* The most commone purpose of targeted attacks is intelligence gathering and the most common method is spear phishing
* Connected cameras were the other most attacked IoT device

### Describe the process of performing dynamic analysis on malware THIS NEEDS TO BE EXPANDED
The difficulty with performing dynamic analysis on malware is that the environment needs to be controlled and contained so the malware can't cause any damage but still needs to seem real so that the malware can't detect that it is being studied. Therefore it needs to have internet access and the ability to contact external sites. Running the malware in a VM may not be sufficient because the malware may detect it is in a VM and shut down. Of course some malware needs to run in a VM to attack cloud computing, but this is unknown before running the program. AV software can't be present because malware may attempt to detect AV software and act differently. Malware is usually targeted at a specific OS so one must test each OS to see which OS the malware is targeting. The malware also may rely on certain exploits in various libraries and system level programs so assuming this malware was taken from an actual environment the test environment must replicate the real environment as closely as possible. Any dependencies must be the same version and patch level. Some malware requires specific hardware so the test environment must use the same hardware as well. Furthermore because the malware needs to be run on a clean environment every time the study environment must be easy to reset. For VM's this is simply done by resetting to a clean snapshot. For malware that must be tested on a real machine the person studying the malware must either reimage the OS or for smaller changes revert modified files to the clean version. 
Some malware is aimed at wide scale deployment and not aimed at just a specific 

### How do botnets use DNS to their advantage 
One way to try and shut down a bot net is to ban the IPs that are used as Command and Control centers. To combat this, malware takes advantage of DNS to circumvent the IP bans. Multiple IP addresses are mapped to the same domain name so the malware can refer to the command and control center via hostname and let DNS circumvent the IP ban. The registry doesn't remove the domain name because bot owners will just register a new one and the registry operators will do so to remain in business. This form of circumvention is called IP fluxing. 

One form of IP fluxing is single flux. In this flavor of fluxing the malicious actor registers hundreds or thousands of IP addresses with the same hostname and the IP addresses are registered and deregistered repeatedly. This is implemented using round robin allocation and short time to live values.

The second form of IP fluxing is called double fluxing. This not only fluxes the IP addresses associated with the domain names but also fluxes the IP addresses of the DNS servers that perform the domain name lookups.

Another method used by botnets to circumvent controls is domain fluxing. Domain fluxing is the inverse of IP fluxing. Many different domain names are registered to the same IP address. The domain fluxing abuses the DNS property that many domains can be registered to the same IP addresses. For instance \*.damballa.com covers both adnthinog.damballa.com and zzzzzzzzz.damballa.com. By having each compromised machine access a unique domain name the botnet operator can identify a victim, track success with different delivery techniques, and bypass anti spam filters. 

The second flavor of domain fluxing is called Domain generation algorithms. This is used to prevent investigation and to make it hard to blacklist domains. In this technique the malware generates a new set of domain names every day and attempts to contact C&C infrastructure and these seemingly random domains. Typically these are only used for a single day so the high turnover makes it very hard to track and prevent this sort of communication. 

In conclusion botnets abuse DNS to find the command and control infrastructure. Fluxing the DNS records in different ways provides varying degrees of resilience to shutdown. 
























