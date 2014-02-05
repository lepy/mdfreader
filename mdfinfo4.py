# -*- coding: utf-8 -*-
""" Measured Data Format blocks paser for version 4.x
Created on Sun Dec 15 12:57:28 2013

:Author: `Aymeric Rateau <http://code.google.com/p/mdfreader/>`__

"""

from struct import calcsize, unpack
from sys import version_info
PythonVersion=version_info
PythonVersion=PythonVersion[0]

#datatypes
LINK='<Q' 
REAL='<d'
BOOL='<h'
UINT8='<B'
BYTE='<c'
INT16='<h'
UINT16='<H'
UINT32='<I'
INT32='<i'
UINT64='<Q'
INT64='<q'
CHAR='<c'

class MDFBlock(dict):
    """MDFBlock base class for the MDF related block classes 
    
    **Methods**
    
    *mdfblockread* : converts a byte array to a given data type
    
    **Attributes**
    
    none        
     
    """
    
    def __init__(self):
        self['id']={}
        self['reserved']={}
        self['length']={}
        self['link_count']={}
    
    def loadHeader(self, fid,  pointer):
        #All blocks have the same header
        if pointer != 0 and not pointer == None:
            fid.seek( pointer )
            self['id']=self.mdfblockreadCHAR(fid, 4)
            self['reserved']=self.mdfblockreadBYTE(fid, 4)
            self['length']=self.mdfblockread(fid, UINT64, 1)
            self['link_count']=self.mdfblockread(fid, UINT64, 1)
        
    @staticmethod
    def mdfblockread( fid, type,  count ):
        # reads value in file corresponding to format and size
        value=fid.read(calcsize(type)*count)
        if value:
            value=unpack( type,value)
            value=value[0]
        else:
            value=None
        return value
        
    @staticmethod
    def mdfblockreadCHAR( fid,  count ):
        # reads value in file corresponding to format and size
        value=fid.read( count )
        if PythonVersion<3:
            value.replace('\x00', '')
        else:
            value.decode('iso8859-1', 'replace').replace('\x00', '') 
        return value
        
    @staticmethod
    def mdfblockreadBYTE( fid, count ):
        # UTF-8 encoded bytes
        value=fid.read( count )
        value.decode('UTF-8', 'replace').replace('\x00', '') 
        return value
        
class IDBlock(MDFBlock):
    def __init__(self, fid):
    # reads IDBlock
        fid.seek(0)
        self['id_file']=self.mdfblockreadCHAR(fid, 8)
        self['id_vers']=self.mdfblockreadCHAR(fid, 8)
        self['id_prog']=self.mdfblockreadCHAR(fid, 8)
        self['id_reserved1']=self.mdfblockreadBYTE(fid, 4)
        self['id_ver']=self.mdfblockread(fid, UINT16, 1)
        self['id_reserved2']=self.mdfblockreadBYTE(fid, 34)

class HDBlock(MDFBlock):
    def __init__(self, fid,  pointer=64):
        # block header
        self.loadHeader(fid, pointer)
        # header block
        self['hd_dg_first']=self.mdfblockread(fid, LINK, 1)
        self['hd_fh_first']=self.mdfblockread(fid, LINK, 1)
        self['hd_ch_first']=self.mdfblockread(fid, LINK, 1)
        self['hd_at_first']=self.mdfblockread(fid, LINK, 1)
        self['hd_ev_first']=self.mdfblockread(fid, LINK, 1)
        self['hd_md_comment']=self.mdfblockread(fid, LINK, 1)
        self['hd_start_time_ns']=self.mdfblockread(fid, UINT64, 1)
        self['hd_tz_offset_min']=self.mdfblockread(fid, INT16, 1)
        self['hd_dst_offset_min']=self.mdfblockread(fid, INT16, 1)
        self['hd_time_flags']=self.mdfblockread(fid, UINT8, 1)
        self['hd_time_class']=self.mdfblockread(fid, UINT8, 1)
        self['hd_flags']=self.mdfblockread(fid, UINT8, 1)
        self['hd_reserved']=self.mdfblockreadBYTE(fid, 1)
        self['hd_start_angle_rad']=self.mdfblockread(fid, REAL, 1)
        self['hd_start_distance']=self.mdfblockread(fid, REAL, 1)
        if self['hd_md_comment']: # if comments exist
            self['Comment']=CommentBlock(fid, self['hd_md_comment'], 'HD')

class FHBlock(MDFBlock):
    def __init__(self, fid,  pointer):
        # block header
        self.loadHeader(fid, pointer)
        # history block
        self['fh_fh_next']=self.mdfblockread(fid, LINK, 1)
        self['fh_md_comment']=self.mdfblockread(fid, LINK, 1)
        self['fh_time_ns']=self.mdfblockread(fid, UINT64, 1)
        self['fh_tz_offset_min']=self.mdfblockread(fid, UINT16, 1)
        self['fh_dst_offset_min']=self.mdfblockread(fid, UINT16, 1)
        self['fh_time_flags']=self.mdfblockread(fid, UINT8, 1)
        self['fh_reserved']=self.mdfblockreadBYTE(fid, 3)
        if self['fh_md_comment']: # comments exist
            self['Comment']=CommentBlock(fid, self['fh_md_comment'], 'FH')
            
class CHBlock(MDFBlock):
    def __init__(self, fid,  pointer):
        # block header
        self.loadHeader(fid, pointer)
        # Channel hierarchy block
        self['ch_ch_next']=self.mdfblockread(fid, LINK, 1)
        self['ch_ch_first']=self.mdfblockread(fid, LINK, 1)
        self['ch_tx_name']=self.mdfblockread(fid, LINK, 1)
        self['ch_md_comment']=self.mdfblockread(fid, LINK, 1)
        self['ch_element']=self.mdfblockread(fid, LINK, (self['link_count']-4)/3)
        # data section
        self['ch_element_count']=self.mdfblockread(fid, LINK, 1)
        self['ch_type']=self.mdfblockread(fid, UINT8, 1)
        self['ch_reserved']=self.mdfblockreadBYTE(fid, 3)
        if self['ch_md_comment']: # comments exist
            self['Comment']=CommentBlock(fid, self['ch_md_comment'])
        if self['ch_tx_name']: # text block containing name of hierarchy level
            self['ch_name_level']=CommentBlock(fid, self['ch_tx_name'])

class CommentBlock(MDFBlock):
    def __init__(self, fid,  pointer, MDType=None):
        if pointer>0:
            # block header
            self.loadHeader(fid, pointer)
            if self['id']=='##MD':
                # Metadata block
                self['Comment']=self.mdfblockreadBYTE(fid, self['length']-24).replace('\x00', '') # removes 0 end 
                from xml.etree.ElementTree import XML
                # remove namespace from xml string
                tmp=self['Comment'].replace("xmlns='http://www.asam.net/mdf/v4'",'')
                tmp=tmp.replace('xmlns=' '"http://www.asam.net/mdf/v4"','')
                #parse xml
                self['xml_tree']=XML(tmp)
                self['xml']=elementTreeToDict(self['xml_tree'])
                # specific action per comment block type, extracts specific tags from xml
                if MDType=='CN': # channel comment
                    pass
                elif MDType=='unit': # channel comment
                    self['unit']=self['xml_tree'].find('TX').text
                elif MDType=='HD': # header comment
                    self['TX']=self['xml_tree'].find('TX').text
                    tmp=self['xml_tree'].find('common_properties')
                    if len(tmp)>=4:
                        self[tmp[0].items()[0][1]]=tmp[0].text # subject
                        self[tmp[1].items()[0][1]]=tmp[1].text # project
                        self[tmp[2].items()[0][1]]=tmp[2].text # department
                        self[tmp[3].items()[0][1]]=tmp[3].text # author
                elif MDType=='FH': # File History comment
                    self['TX']=self['xml_tree'].find('TX').text
                    self['tool_id']=self['xml_tree'].find('tool_id').text
                    self['tool_vendor']=self['xml_tree'].find('tool_vendor').text
                    self['tool_version']=self['xml_tree'].find('tool_version').text
                    self['user_name']=self['xml_tree'].find('user_name').text
            elif self['id']=='##TX':
                if MDType=='CN': # channel comment
                    self['name']=self.mdfblockreadBYTE(fid, self['length']-24).replace('\x00', '')
                else:
                    self['Comment']=self.mdfblockreadBYTE(fid, self['length']-24).replace('\x00', '')
    
def elementTreeToDict(element):
    #converts xml into dictionnary
    node = dict()

    text = getattr(element, 'text', None)
    if text is not None:
        node['text'] = text

    node.update(element.items()) # element's attributes

    child_nodes = {}
    for child in element: # element's children
        child_nodes.setdefault(child, []).append( elementTreeToDict(child) )

    # convert all single-element lists into non-lists
    for key, value in child_nodes.items():
        if len(value) == 1:
             child_nodes[key] = value[0]

    node.update(child_nodes.items())

    return node
    
class DGBlock(MDFBlock):
    def __init__(self, fid,  pointer):
        # block header
        self.loadHeader(fid, pointer)
        # Data Group block : Links
        self['dg_dg_next']=self.mdfblockread(fid, LINK, 1)
        self['dg_cg_first']=self.mdfblockread(fid, LINK, 1)
        self['dg_data']=self.mdfblockread(fid, LINK, 1)
        self['dg_md_comment']=self.mdfblockread(fid, LINK, 1)
        # data section
        self['dg_rec_id_size']=self.mdfblockread(fid, UINT8, 1)
        self['dg_reserved']=self.mdfblockreadBYTE(fid, 7)
        if self['dg_md_comment']: # comments exist
            self['Comment']=CommentBlock(fid, self['dg_md_comment'])
        
class CGBlock(MDFBlock):
    def __init__(self, fid,  pointer):
        # block header
        self.loadHeader(fid, pointer)
        # Channel Group block : Links
        self['cg_cg_next']=self.mdfblockread(fid, LINK, 1)
        self['cg_cn_first']=self.mdfblockread(fid, LINK, 1)
        self['cg_tx_acq_name']=self.mdfblockread(fid, LINK, 1)
        self['cg_si_acq_source']=self.mdfblockread(fid, LINK, 1)
        self['cg_sr_first']=self.mdfblockread(fid, LINK, 1)
        self['cg_md_comment']=self.mdfblockread(fid, LINK, 1)
        # data section
        self['cg_record_id']=self.mdfblockread(fid, UINT64, 1)
        self['cg_cycle_count']=self.mdfblockread(fid, UINT64, 1)
        self['cg_flags']=self.mdfblockread(fid, UINT16, 1)
        self['cg_path_separator']=self.mdfblockread(fid, UINT16, 1)
        self['cg_reserved']=self.mdfblockreadBYTE(fid, 4)
        self['cg_data_bytes']=self.mdfblockread(fid, UINT32, 1)
        self['cg_invalid_bytes']=self.mdfblockread(fid, UINT32, 1)
        if self['cg_md_comment']: # comments exist
            self['Comment']=CommentBlock(fid, self['cg_md_comment'])
        if self['cg_tx_acq_name']: # comments exist
            self['acq_name']=CommentBlock(fid, self['cg_tx_acq_name'])
        
class CNBlock(MDFBlock):
    def __init__(self, fid,  pointer,  attachmentNumber=None):
        if pointer != 0 and not pointer == None:
            fid.seek( pointer )
            self['id']=self.mdfblockreadCHAR(fid, 4)
            self['reserved']=self.mdfblockreadBYTE(fid, 4)
            self['length']=self.mdfblockread(fid, UINT64, 1)
            self['link_count']=self.mdfblockread(fid, UINT64, 1)
            # data section
            fid.seek(pointer+self['length']-71)
            self['cn_type']=self.mdfblockread(fid, UINT8, 1)
            self['cn_sync_type']=self.mdfblockread(fid, UINT8, 1)
            self['cn_data_type']=self.mdfblockread(fid, UINT8, 1)
            self['cn_bit_offset']=self.mdfblockread(fid, UINT8, 1)
            self['cn_byte_offset']=self.mdfblockread(fid, UINT32, 1)
            self['cn_bit_count']=self.mdfblockread(fid, UINT32, 1)
            self['cn_flags']=self.mdfblockread(fid, UINT32, 1)
            self['cn_invalid_bit_pos']=self.mdfblockread(fid, UINT32, 1)
            self['cn_precision']=self.mdfblockread(fid, UINT8, 1)
            self['cn_reserved']=self.mdfblockreadBYTE(fid, 1)
            self['cn_attachment_count']=self.mdfblockread(fid, UINT16, 1)
            self['cn_val_range_min']=self.mdfblockread(fid, REAL, 1)
            self['cn_val_range_max']=self.mdfblockread(fid, REAL, 1)
            self['cn_limit_min']=self.mdfblockread(fid, REAL, 1)
            self['cn_limit_max']=self.mdfblockread(fid, REAL, 1)
            self['cn_limit_ext_min']=self.mdfblockread(fid, REAL, 1)
            self['cn_limit_ext_max']=self.mdfblockread(fid, REAL, 1)
            # Channel Group block : Links
            fid.seek(pointer+24)
            self['cn_cn_next']=self.mdfblockread(fid, LINK, 1)
            self['cn_composition']=self.mdfblockread(fid, LINK, 1)
            self['cn_tx_name']=self.mdfblockread(fid, LINK, 1)
            self['cn_si_source']=self.mdfblockread(fid, LINK, 1)
            self['cn_cc_conversion']=self.mdfblockread(fid, LINK, 1)
            self['cn_data']=self.mdfblockread(fid, LINK, 1)
            self['cn_md_unit']=self.mdfblockread(fid, LINK, 1)
            self['cn_md_comment']=self.mdfblockread(fid, LINK, 1)
            if self['cn_attachment_count']>0:
                self['cn_at_reference']=self.mdfblockread(fid, LINK, self['cn_attachment_count'])
                for at in range(self['cn_attachment_count']):
                    self['attachment'][at]=ATBlock(fid, self['cn_at_reference'][at])
            if self['link_count']>(8+self['cn_attachment_count']):
                self['cn_default_x']=self.mdfblockread(fid, LINK, 3)
            else:
                self['cn_default_x']=None
            if self['cn_md_comment']: # comments exist
                self['Comment']=CommentBlock(fid, self['cn_md_comment'])
            if self['cn_md_unit']: # comments exist
                self['unit']=CommentBlock(fid, self['cn_md_unit'], 'unit')
            if self['cn_tx_name']: # comments exist
                self['name']=CommentBlock(fid, self['cn_tx_name'], 'CN')['name']

class CCBlock(MDFBlock):
    def __init__(self, fid,  pointer):
        # block header
        if pointer != 0 and not pointer == None:
            fid.seek( pointer )
            self['id']=self.mdfblockreadCHAR(fid, 4)
            self['reserved']=self.mdfblockreadBYTE(fid, 4)
            self['length']=self.mdfblockread(fid, UINT64, 1)
            self['link_count']=self.mdfblockread(fid, UINT64, 1)
            # Channel Conversion block : Links
            self['cc_tx_name']=self.mdfblockread(fid, LINK, 1)
            self['cc_md_unit']=self.mdfblockread(fid, LINK, 1)
            self['cc_md_comment']=self.mdfblockread(fid, LINK, 1)
            self['cc_cc_inverse']=self.mdfblockread(fid, LINK, 1)
            self['cc_ref']=self.mdfblockread(fid, LINK, self['link_count']-4)
            # data section
            self['cc_type']=self.mdfblockread(fid, UINT8, 1)
            self['cc_precision']=self.mdfblockread(fid, UINT8, 1)
            self['cc_flags']=self.mdfblockread(fid, UINT16, 1)
            self['cc_ref_count']=self.mdfblockread(fid, UINT16, 1)
            self['cc_val_count']=self.mdfblockread(fid, UINT16, 1)
            self['cc_phy_range_min']=self.mdfblockread(fid, REAL, 1)
            self['cc_phy_range_max']=self.mdfblockread(fid, REAL, 1)
            if self['cc_val_count']:
                self['cc_val']=self.mdfblockread(fid, REAL, self['cc_val_count'])
            if self['cc_type']==3: # reads Algebraic formula
                self['cc_ref']=CommentBlock(fid, self['cc_ref'])
            elif self['cc_type']in (7, 8, 9, 10): # text list
                for i in range(self['cc_ref_count']):
                    temp=CommentBlock(fid, self['cc_ref'][i])
                    self['cc_ref'][i]=temp['name']
            if self['cc_md_comment']: # comments exist
                self['Comment']=CommentBlock(fid, self['cc_md_comment'])
            if self['cc_md_unit']: # comments exist
                self['unit']=CommentBlock(fid, self['cc_md_unit'])
            if self['cc_tx_name']: # comments exist
                self['name']=CommentBlock(fid, self['cc_tx_name'])
        else: # no conversion
            self['cc_type']=0

class CABlock(MDFBlock):
    def __init__(self, fid,  pointer):
        # block header
        if pointer != 0 and not pointer == None:
            fid.seek( pointer )
            self['id']=self.mdfblockreadCHAR(fid, 4)
            self['reserved']=self.mdfblockreadBYTE(fid, 4)
            self['length']=self.mdfblockread(fid, UINT64, 1)
            self['link_count']=self.mdfblockread(fid, UINT64, 1)
            # reads data section
            fid.seek( pointer +24 + self['link_count']*8)
            self['ca_type']=self.mdfblockread(fid, UINT8, 1) 
            self['ca_storage']=self.mdfblockread(fid, UINT8, 1) 
            self['ca_ndim']=self.mdfblockread(fid, UINT16, 1) 
            self['ca_flags']=int(self.mdfblockread(fid, UINT32, 1) )
            self['ca_byte_offset_base']=self.mdfblockread(fid, INT32, 1) 
            self['ca_invalid_bit_pos_base']=self.mdfblockread(fid, UINT32, 1)
            self['ca_dim_size']=self.mdfblockread(fid, UINT64, self['ca_ndim'])
            if 1<<5 & self['ca_flags']: # bit5
                self['ca_axis_value']=self.mdfblockread(fid, REAL, self['ca_dim_size'].sum())
            if self['ca_storage']>=1:
                self['ca_cycle_count']=self.mdfblockread(fid, UINT64, self['ca_dim_size'].product())
            # Channel Conversion block : Links
            fid.seek( pointer +24 )
            self['ca_composition']=self.mdfblockread(fid, LINK, 1) # point to CN for array of structures or CA for array of array
            if self['ca_storage']==2:
                self['ca_data']=self.mdfblockread(fid, LINK, self['ca_dim_size'].product()) 
            if 1<<0 &self['ca_flags']: # bit 0
                self['ca_dynamic_size']=self.mdfblockread(fid, LINK, self['ca_ndim']*3)
            if 1<<1 &self['ca_flags']: # bit 1
                self['ca_input_quantity']=self.mdfblockread(fid, LINK, self['ca_ndim']*3)
            if 1<<2 &self['ca_flags']: # bit 2
                self['ca_output_quantity']=self.mdfblockread(fid, LINK, 3)
            if 1<<3 &self['ca_flags']: # bit 3
                self['ca_comparison_quantity']=self.mdfblockread(fid, LINK, 3)
            if 1<<4 &self['ca_flags']: # bit 4
                self['ca_cc_axis_conversion']=self.mdfblockread(fid, LINK, self['ca_ndim'])
            if 1<<4 &self['ca_flags'] and 1<<5 &self['ca_flags']: # bit 4 and 5
                self['ca_axis']=self.mdfblockread(fid, LINK, self['ca_ndim']*3)

class ATBlock(MDFBlock):
    def __init__(self, fid,  pointer):
        # block header
        if pointer != 0 and not pointer == None:
            fid.seek( pointer )
            self['id']=self.mdfblockreadCHAR(fid, 4)
            self['reserved']=self.mdfblockreadBYTE(fid, 4)
            self['length']=self.mdfblockread(fid, UINT64, 1)
            self['link_count']=self.mdfblockread(fid, UINT64, 1)
            # links
            self['at_at_next']=self.mdfblockread(fid, LINK, 1)
            self['at_tx_filename']=self.mdfblockread(fid, LINK, 1)
            self['at_tx_mimetype']=self.mdfblockread(fid, LINK, 1)
            self['at_md_comment']=self.mdfblockread(fid, LINK, 1)
            # data
            self['at_flags']=self.mdfblockread(fid, UINT16, 1)
            self['at_creator_index']=self.mdfblockread(fid, UINT16, 1)
            self['at_reserved']=self.mdfblockreadBYTE(fid, 4)
            self['at_md5_checksum']=self.mdfblockreadBYTE(fid, 16)
            self['at_original_size']=self.mdfblockread(fid, UINT64, 1)
            self['at_embedded_size']=self.mdfblockread(fid, UINT64, 1)
            if self['at_embedded_size']>0:
                self['at_embedded_data']=self.mdfblockreadBYTE(fid, self['at_embedded_size'])
            if self['at_md_comment']: # comments exist
                self['Comment']=CommentBlock(fid, self['at_md_comment'])
        
class EVBlock(MDFBlock):
    def __init__(self, fid,  pointer):
        # block header
        if pointer != 0 and not pointer == None:
            fid.seek( pointer )
            self['id']=self.mdfblockreadCHAR(fid, 4)
            self['reserved']=self.mdfblockreadBYTE(fid, 4)
            self['length']=self.mdfblockread(fid, UINT64, 1)
            self['link_count']=self.mdfblockread(fid, UINT64, 1)
            #data section
            fid.seek( pointer +self['length']-32)
            self['ev_type']=self.mdfblockread(fid, UINT8, 1)
            self['ev_sync_type']=self.mdfblockread(fid, UINT8, 1)
            self['ev_range_type']=self.mdfblockread(fid, UINT8, 1)
            self['ev_cause']=self.mdfblockread(fid, UINT8, 1)
            if self['ev_cause']==0:
                self['ev_cause']='OTHER'
            elif self['ev_cause']==1:
                self['ev_cause']=='ERROR'
            elif self['ev_cause']==2:
                self['ev_cause']=='TOOL'
            elif self['ev_cause']==3:
                self['ev_cause']=='SCRIPT'
            elif self['ev_cause']==4:
                self['ev_cause']=='USER'
            self['ev_flags']=self.mdfblockread(fid, UINT8, 1)
            self['at_reserved']=self.mdfblockreadBYTE(fid, 3)
            self['ev_scope_count']=self.mdfblockread(fid, UINT32, 1)
            self['ev_attachment_count']=self.mdfblockread(fid, UINT16, 1)
            self['ev_creator_index']=self.mdfblockread(fid, UINT16, 1)
            self['ev_sync_base_value']=self.mdfblockread(fid, UINT64, 1)
            self['ev_sync_factor']=self.mdfblockread(fid, REAL, 1)
            # link section
            fid.seek( pointer +24)
            self['ev_ev_next']=self.mdfblockread(fid, LINK, 1)
            self['ev_ev_parent']=self.mdfblockread(fid, LINK, 1)
            self['ev_ev_range']=self.mdfblockread(fid, LINK, 1)
            self['ev_tx_name']=self.mdfblockread(fid, LINK, 1)
            self['ev_md_comment']=self.mdfblockread(fid, LINK, 1)
            self['ev_scope']=self.mdfblockread(fid, LINK, self['ev_scope_count'])
            # post treatment
            if self['ev_attachment_count']>0:
                self['ev_at_reference']=self.mdfblockread(fid, LINK, self['ev_attachment_count'])
                for at in range(self['ev_attachment_count']):
                    self['attachment'][at]=ATBlock(fid, self['ev_at_reference'][at])
            if self['ev_md_comment']: # comments exist
                self['Comment']=CommentBlock(fid, self['ev_md_comment'])
            if self['ev_tx_name']: # comments exist
                self['name']=CommentBlock(fid, self['ev_tx_name'])

class SRBlock(MDFBlock):
    def __init__(self, fid,  pointer):
        # block header
        if pointer != 0 and not pointer == None:
            fid.seek( pointer )
            self['id']=self.mdfblockreadCHAR(fid, 4)
            self['reserved']=self.mdfblockreadBYTE(fid, 4)
            self['length']=self.mdfblockread(fid, UINT64, 1)
            self['link_count']=self.mdfblockread(fid, UINT64, 1)
            # link section
            self['sr_sr_next']=self.mdfblockread(fid, LINK, 1)
            self['sr_data']=self.mdfblockread(fid, LINK, 1)
            # data section
            self['sr_cycle_count']=self.mdfblockread(fid, UINT64, 1)
            self['sr_interval']=self.mdfblockread(fid, REAL, 1)
            self['sr_sync_type']=self.mdfblockread(fid, UINT8, 1)
            self['sr_flags']=self.mdfblockread(fid, UINT8, 1)
            self['sr_reserved']=self.mdfblockreadBYTE(fid, 6)
            
class SIBlock(MDFBlock):
    def __init__(self, fid,  pointer):
        # block header
        if pointer != 0 and not pointer == None:
            fid.seek( pointer )
            self['id']=self.mdfblockreadCHAR(fid, 4)
            self['reserved']=self.mdfblockreadBYTE(fid, 4)
            self['length']=self.mdfblockread(fid, UINT64, 1)
            self['link_count']=self.mdfblockread(fid, UINT64, 1)
            # link section
            self['si_tx_name']=self.mdfblockread(fid, LINK, 1)
            self['si_tx_path']=self.mdfblockread(fid, LINK, 1)
            self['si_md_comment']=self.mdfblockread(fid, LINK, 1)
            # data section
            self['si_type']=self.mdfblockread(fid, UINT8, 1)
            if self['si_type']==0:
                self['si_type']='OTHER' # unknown
            elif self['si_type']==1:
                self['si_type']='ECU'
            elif self['si_type']==2:
                self['si_type']='BUS'
            elif self['si_type']==3:
                self['si_type']='I/O'
            elif self['si_type']==4:
                self['si_type']='TOOL'
            elif self['si_type']==5:
                self['si_type']='USER'
            self['si_bus_type']=self.mdfblockread(fid, UINT8, 1)
            if self['si_bus_type']==0:
                self['si_bus_type']='NONE'
            elif self['si_bus_type']==1:
                self['si_bus_type']='OTHER'
            elif self['si_bus_type']==2:
                self['si_bus_type']='CAN'
            elif self['si_bus_type']==3:
                self['si_bus_type']='LIN'
            elif self['si_bus_type']==4:
                self['si_bus_type']='MOST'
            elif self['si_bus_type']==5:
                self['si_bus_type']='FLEXRAY'
            elif self['si_bus_type']==6:
                self['si_bus_type']='K_LINE'
            elif self['si_bus_type']==7:
                self['si_bus_type']='ETHERNET'
            elif self['si_bus_type']==8:
                self['si_bus_type']='USB'
            self['si_flags']=self.mdfblockread(fid, UINT8, 1)
            self['si_reserved']=self.mdfblockreadBYTE(fid, 5)
            # post treatment
            self['source_name']=self.CommentBlock(fid, self['si_tx_name'])
            self['source_path']=self.CommentBlock(fid, self['si_tx_path'])
            self['comment']=self.CommentBlock(fid, self['si_md_comment'])
            
class info4(dict):
    def __init__(self, fileName=None, fid=None):
        self['IDBlock'] = {} # Identifier Block
        self['HDBlock'] = {} # Header Block
        self['FHBlock'] = {}
        self['CHBlock'] = {}
        self['DGBlock']= {} # Data Group Block
        self['CGBlock'] = {} # Channel Group Block
        self['CNBlock'] = {}# Channel Block
        self['CCBlock'] = {} # Conversion block
        self['ATBlock'] = {} # Attachment block
        self.fileName = fileName
        if fileName != None and fid==None:
            try:
                fid = open( self.fileName, 'rb' )
            except IOError:
                print('Can not find file'+self.fileName)
                raise
            self.readinfo( fid )
            # CLose the file
            fid.close()
        elif fileName == None and fid!=None:
            self.readinfo(fid)

    def readinfo(self, fid):
        # this function reads all blocks contained in mdf4 file
        
        # reads IDBlock
        self['IDBlock'].update(IDBlock(fid))
        
        # reads Header HDBlock
        self['HDBlock'].update(HDBlock(fid))        
        
        # reads File History blocks, always exists
        fh=0 # index of fh blocks
        self['FHBlock'][fh] = {}
        self['FHBlock'][fh] .update(FHBlock(fid, self['HDBlock']['hd_fh_first']))
        while self['FHBlock'][fh]['fh_fh_next']:
            self['FHBlock'][fh] .update(FHBlock(fid, self['FHBlock'][fh]['fh_fh_next']))
            fh+=1
        
        # reads Channel Hierarchy blocks
        if self['HDBlock']['hd_ch_first']:
            ch=0
            self['CHBlock'][ch] = {}
            self['CHBlock'][ch] .update(CHBlock(fid, self['HDBlock']['hd_ch_first']))
            while self['CHBlock'][ch]['ch_ch_next']:
                self['CHBlock'][ch] .update(CHBlock(fid, self['CHBlock'][ch]['ch_ch_next']))
                ch+=1
        
        # reads Attachment block
        self['ATBlock']=self.readATBlock(fid, self['HDBlock']['hd_at_first'])
        
        # reads Event Block
        if self['HDBlock']['hd_ev_first']:
            ev=0
            self['EVBlock'][ev] = {}
            self['EVBlock'][ev] .update(EVBlock(fid, self['HDBlock']['hd_ev_first']))
            while self['EVBlock'][ev]['ev_ev_next']:
                self['EVBlock'][ev] .update(EVBlock(fid, self['EVBlock'][ev]['ev_ev_next']))
                ev+=1
        
        # reads Data Group Blocks and recursively the other related blocks
        self.readDGBlock(fid)

    def readDGBlock(self, fid, channelNameList=False):
        # reads Data Group Blocks
        if self['HDBlock']['hd_dg_first']:
            dg=0
            self['DGBlock'][dg] = {}
            self['DGBlock'][dg] .update(DGBlock(fid,self['HDBlock']['hd_dg_first']))
            # reads Channel Group blocks
            self.readCGBlock(fid, dg, channelNameList)
            while self['DGBlock'][dg]['dg_dg_next']:
                dg+=1
                self['DGBlock'][dg]={}
                self['DGBlock'][dg].update(DGBlock(fid, self['DGBlock'][dg-1]['dg_dg_next']))
                # reads Channel Group blocks
                self.readCGBlock(fid, dg, channelNameList)
                
    def readCGBlock(self, fid, dg, channelNameList=False):
        # reads Channel Group blocks
        if self['DGBlock'][dg] ['dg_cg_first']:
            cg=0
            self['CGBlock'][dg] = {}
            self['CGBlock'][dg] [cg]={}
            self['CGBlock'][dg][cg].update(CGBlock(fid, self['DGBlock'][dg]['dg_cg_first']))
            
            if not channelNameList:
                # reads Source Information Block
                self['CGBlock'][dg][cg]['SIBlock']=SIBlock(fid, self['CGBlock'][dg][cg]['cg_si_acq_source'])
                
                # reads Sample Reduction Block
                self['CGBlock'][dg][cg]['SRBlock']=self.readSRBlock(fid, self['CGBlock'][dg][cg]['cg_sr_first'])
            
            # reads Channel Block
            self.readCNBlock(fid, dg, cg, channelNameList)
            while self['CGBlock'][dg][cg]['cg_cg_next']:
                cg+=1
                self['CGBlock'][dg][cg]={}
                self['CGBlock'][dg][cg].update(CGBlock(fid, self['CGBlock'][dg][cg-1]['cg_cg_next']))
                if not channelNameList:
                    # reads Source Information Block
                    self['CGBlock'][dg][cg]['SIBlock'].update(SIBlock(fid, self['CGBlock'][dg][cg]['cg_si_acq_source']))
                    
                    # reads Sample Reduction Block
                    self['CGBlock'][dg][cg]['SRBlock'].update(self.readSRBlock(fid, self['CGBlock'][dg][cg]['cg_sr_first']))
                
                # reads Channel Block
                self.readCNBlock(fid, dg, cg, channelNameList)
                
    def readCNBlock(self, fid, dg, cg, channelNameList=False):
        # reads Channel Block
            cn=0
            self['CNBlock'][dg] = {}
            self['CNBlock'][dg][cg] = {}
            self['CNBlock'][dg][cg][cn] = {}
            self['CCBlock'][dg] = {}
            self['CCBlock'][dg][cg] = {}
            self['CCBlock'][dg][cg][cn] = {}
            self['CNBlock'][dg][cg][cn].update(CNBlock(fid, self['CGBlock'][dg][cg]['cg_cn_first']))
            
            if not channelNameList:
                # reads Channel Source Information
                self['CNBlock'][dg][cg][cn]['SIBlock']=SIBlock(fid, self['CNBlock'][dg][cg][cn]['cn_si_source'])
                
                # reads Channel Array Block
                
                # reads Attachment Block
                if self['CNBlock'][dg][cg][cn]['cn_attachment_count']>0:
                    for at in range(self['CNBlock'][dg][cg][cn]['cn_attachment_count']):
                        self['CNBlock'][dg][cg][cn]['attachment'][at].update(self.readATBlock(fid, self['CNBlock'][dg][cg][cn-1]['cn_at_reference'][at]))
            
                # reads Channel Conversion Block
                self['CCBlock'][dg][cg][cn]=CCBlock(fid, self['CNBlock'][dg][cg][cn]['cn_cc_conversion'])
            while self['CNBlock'][dg][cg][cn]['cn_cn_next']:
                cn=cn+1
                self['CNBlock'][dg][cg][cn]={}
                self['CNBlock'][dg][cg][cn].update(CNBlock(fid, self['CNBlock'][dg][cg][cn-1]['cn_cn_next']))
                
                if not channelNameList:
                    # reads Channel Source Information
                    self['CNBlock'][dg][cg][cn]['SIBlock']=SIBlock(fid, self['CNBlock'][dg][cg][cn]['cn_si_source'])
                    
                    # reads Channel Array Block
                    
                    # reads Attachment Block
                    if self['CNBlock'][dg][cg][cn-1]['cn_attachment_count']>0:
                        for at in range(self['CNBlock'][dg][cg][cn-1]['cn_attachment_count']):
                            self['CNBlock'][dg][cg][cn-1]['attachment'][at].update(self.readATBlock(fid, self['CNBlock'][dg][cg][cn-1]['cn_at_reference'][at]))
                    
                    # reads Channel Conversion Block
                    self['CCBlock'][dg][cg][cn]=CCBlock(fid, self['CNBlock'][dg][cg][cn]['cn_cc_conversion'])
    
    def readSRBlock(self, fid, pointer):
        # reads Sample Reduction Blocks
        if pointer>0:
            sr=0
            srBlocks={}
            srBlocks[sr].update(SRBlock(fid, pointer))
            while srBlocks[sr]['sr_sr_next']>0:
                srBlocks[sr].update(SRBlock(fid, srBlocks[sr]['sr_sr_next']))
                sr+=1
            return srBlocks
            
    def readATBlock(selfself, fid, pointer):
        # reads Attachment blocks
        if pointer >0:
            at=0
            atBlocks={}
            atBlocks[at].update(ATBlock(fid, pointer))
            while atBlocks[at]['at_at_next']>0:
                atBlocks[at].update(ATBlock(fid, atBlocks[at]['at_at_next']))
                at+=1
            return atBlocks
    
    def listChannels( self, fileName = None ):
        # Read MDF file and extract its complete structure
        if not fileName == None:
            self.fileName = fileName
        # Open file
        fid = open( self.fileName, 'rb' )
        channelNameList=[]
        # reads Header HDBlock
        self['HDBlock'].update(HDBlock(fid))
            
        # reads Data Group, channel groups and channel Blocks  recursively but not the other metadata block
        self.readDGBlock(fid, True)
        
        for dg in self['DGBlock'].keys():
            for cg in self['CGBlock'][dg].keys():
                for cn in self['CNBlock'][dg][cg].keys():
                    channelNameList.append(self['CNBlock'][dg][cg][cn]['name']['name'])
        
        # CLose the file
        fid.close()
        return channelNameList