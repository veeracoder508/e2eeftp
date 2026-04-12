# PER 1 - CHANGELOG.md Guidelines
Author: R A Veeraragavan [veeracoder123@gmail.com]

Type: Informational

Topic: Governance

Date Issued: 12 April 2026

# Table of Content
- [Introduction](#introduction)
- [Guidelines](#guidelines)
    * [Creating](#creating)
    * [Tags](#tags)

*****

# Introduction
This PER contains the guidelines for updating and creating the `CHANGELOG.md`.

# Guidelines
These are the guidelines for creating and updating.

## Creating
The preamble is:
```
# CHANGELOG
version: <version number>
type: <beta | alpha | production>
```

## Tags
For every change point in the CHANGELOG.md, there is a tag.
```
**(tag: <name>)**
```
These are all the tags that can be used. 
| name | use |
| ----- | ----- |
| `struct` | change in the project tree structure. |
| `name_scheme` | change in variable, function, or class names. |
| `feature` | addition of a new feature. |
