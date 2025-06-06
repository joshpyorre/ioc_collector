# Build a list of historical IOCs based off a keyword search on abuse.ch, and geo-map it if needed

In this example, I'm searching for darkside:

1. Go to https://threatfox.abuse.ch/browse.php?search=malware%3Adarkside

- Unfortunately, with abuse.ch, you can search for things like ioc:darkside in the browser and it has the info, but because it's old, it's only in the browser interface. Only new/unarchived stuff is queryable via the API.
- To get the data, you have to copy the table, like copy it into your clipboard and paste it into a text file so it looks like this:

```
2024-07-27 16:06	http://darksidfqzcuhtk2.onion/2AHUVJ3VGS97NUG5J5EYMQM5PJO77V9V0GDT3UYIJGFZUTOQRLUX593CQ2EZ2ZEH	 DarkSide	darkside	 nickkuechel
2024-07-27 16:06	http://darksidedxcftmqa.onion/polifilm/AWeu5Sv7zTTCTjZD8YkgoPRznfE5r7G-vbsXok9EvfiaNL_eDwRlgRMruMHisnEF	 DarkSide	darkside	 nickkuechel
2022-08-01 01:00	98272cada9caf84c31d70fdc3705e95ef73cb4a5c507e2cf3caee1893a7a6f63	 DarkSide	darkside	 nickkuechel
2022-04-27 14:49	0c1f2f914e5b512df229ffea8a27078ddcf992eb175fc05d02aa3bc3fe29a932	 DarkSide	darkside	 nickkuechel
2022-04-15 14:03	2d82be244e23001148ed5a6d83856b6f7cd20c3f7786481303d5d584c51ff5f0	 DarkSide	darkside Ransomware	 nickkuechel
2022-02-12 00:43	http://darksidfqzcuhtk2.onion/DZYNTXY9RP5P8DQ96EFKV2YTOVAMA3VVHL5V0RASUBLBWZGLG51U4LOOBSHV9R0Y	 DarkSide	darkside	 nickkuechel
2022-02-12 00:42	43e61519be440115eeaa3738a0e4aa4bb3c8ac5f9bdfce1a896db17a374eb8aa	 DarkSide	darkside	 nickkuechel
```

Save that text file and go to the next step.

2. Run the following script to look up SHA256 items in VirusTotal. 
- You will need to enter your VT key at the top of the script. 
- It takes a moment to run depending on how many items you have in the list. It's recommended to pipe the output to a new file:

`python3 parse_text_from_abuse_ch_and_VTlookup.py darkside_raw.txt > darkside_raw_vt_results.txt`

3. darkside_raw_vt_results.txt will look like this:

```
2024-07-27 16:06,http://darksidfqzcuhtk2.onion/2AHUVJ3VGS97NUG5J5EYMQM5PJO77V9V0GDT3UYIJGFZUTOQRLUX593CQ2EZ2ZEH,darksidfqzcuhtk2.onion,darkside
2024-07-27 16:06,http://darksidedxcftmqa.onion/polifilm/AWeu5Sv7zTTCTjZD8YkgoPRznfE5r7G-vbsXok9EvfiaNL_eDwRlgRMruMHisnEF,darksidedxcftmqa.onion,darkside
2022-08-01 01:00,98272cada9caf84c31d70fdc3705e95ef73cb4a5c507e2cf3caee1893a7a6f63,98272cada9caf84c31d70fdc3705e95ef73cb4a5c507e2cf3caee1893a7a6f63,darkside
2022-08-01 01:00,13.107.4.50,MICROSOFT-CORP-MSN-AS-BLOCK,darkside,country=US,result=harmless,registration_date=2015-03-26T13:58:18-04:00
2022-08-01 01:00,20.99.133.109,MICROSOFT-CORP-MSN-AS-BLOCK,darkside,country=US,result=harmless,registration_date=2017-10-18T13:17:25-04:00
2022-08-01 01:00,23.194.186.99,AKAMAI-AS,darkside,country=US,result=unknown,registration_date=N/A
2022-08-01 01:00,23.32.75.29,Akamai International B.V.,darkside,country=US,result=harmless,registration_date=2011-05-16T15:49:09-04:00
```

The items are: 
- date (from abuse.ch), 
- ip
- ASN owner
- threatname (from your search)
- ASN country
- harmless or malicious (based on AV scans)
- registration date

A note about registration date: This is called event_date (under the event_action: "registration" from the VT results). It refers to the registration date of the IP address allocation within the context of the RDAP (Registration Data Access Protocol) data returned by a Regional Internet Registry (RIR) such as RIPE, ARIN, APNIC, etc.

To do: This only looks up the SHA256. I will modify it soon to get the A record from any URLs/Domains.

# If you want to put the IP's on a map:

1. See the readme in the WEB directory. When the flask app is running, just upload your text file (darkside_raw_vt_results.txt in this example)