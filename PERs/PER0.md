# PER 0 - Index for Protocol Enrichment Rules (PERs)
Author: R A Veeraragavan [veeracoder123@gmail.com]

Type: Informational

Topic: Governance

Date Issued: 12 April 2026

-----

# Table of Content
- [Introduction](#introduction)
- [Guidelines for creating PERs](#guidelines-for-creating-pers)
	* [PER Header Preamble](#per-header-preamble)

*****

# Introduction
This PER contains the index of all Protocol Enhancement Rules, known as PERs. PER numbers are assigned by the PER editors, and once assigned are never changed. The version control history of the PER texts represent their historical record.

# Guidelines for creating PERs
These are the guidelines for creating a PER.

## PER Header Preamble
Each PER must begin with an [RFC 2822](https://datatracker.ietf.org/doc/html/rfc2822.html) style header preamble. The headers must appear in the following order. Headers marked with “*” are optional and are described below. All other headers are required.

```
  PER <PER number> - <PER title>
  Author: <list of authors' names and optionally, email addresses>
  Discussions-To: <URL of current canonical discussion thread>
  Status: <Draft | Active | Accepted | Provisional | Deferred | Rejected |
           Withdrawn | Final | Superseded>
  Type: <Standards Track | Informational | Process>
* Topic: <Governance | Packaging | Release | Typing>
* Requires: <PER numbers>
  Created: <date created on, in alphanumeric format>
* protocol-version: <version number>
  Post-History: <dates, in alphanumeric format,
                 inline-linked to PER discussion threads>
* Replaces: <PER number>
* Superseded-By: <PER number>
* Resolution: <date in alphanumeric format, linked to the acceptance/rejection post>
``` 

The Author header lists the names, and optionally the email addresses of all the authors/owners of the PER. The format of the Author header values must be:
```
R A Veeraragavan [veeracoder123@gmail.com]
```
if the email address is included, and just:
```
R A Veeraragavan
```
if github user name is used:
```
github: veeracoder508
```
if the address is not given. Most PER authors use their real name, but if you prefer a different name and use it consistently in discussions related to the PER, you may use it here.

If there are multiple authors, each should be on a separate line following [RFC 2822](https://datatracker.ietf.org/doc/html/rfc2822.html) continuation line conventions. Note that personal email addresses in PERs will be obscured as a defense against spam harvesters.

The Sponsor field records which developer (core, or otherwise approved by the Steering Council) is sponsoring the PER. If one of the authors of the PER is a core developer then no sponsor is necessary and thus this field should be left out.

The PER-Delegate field is used to record the individual appointed by the Steering Council to make the final decision on whether or not to approve or reject a PER.

The Discussions-To header provides the URL to the current canonical discussion thread for the PER. For email lists, this should be a direct link to the thread in the list’s archives, rather than just a mailto: or hyperlink to the list itself.

The Type header specifies the type of PER: Standards Track, Informational, or Process.

The Created header records the date that the PER was assigned a number, while Post-History is used to record the dates of and corresponding URLs to the Discussions-To threads for the PER, with the former as the linked text, and the latter as the link target. Both sets of dates should be in dd-mmm-yyyy format, e.g. 14-Aug-2001.

Standards Track PERs will typically have a Python-Version header which indicates the version of Python that the feature will be released with. Standards Track PERs without a Python-Version header indicate interoperability standards that will initially be supported through external libraries and tools, and then potentially supplemented by a later PER to add support to the standard library. Informational and Process PERs do not need a Python-Version header.

PERs may have a Requires header, indicating the PER numbers that this PER depends on.

PERs may also have a Superseded-By header indicating that a PER has been rendered obsolete by a later document; the value is the number of the PER that replaces the current document. The newer PER must have a Replaces header containing the number of the PER that it rendered obsolete.
