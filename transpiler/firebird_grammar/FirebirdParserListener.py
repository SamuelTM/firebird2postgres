# Generated from FirebirdParser.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .FirebirdParser import FirebirdParser
else:
    from FirebirdParser import FirebirdParser

# This class defines a complete listener for a parse tree produced by FirebirdParser.
class FirebirdParserListener(ParseTreeListener):

    # Enter a parse tree produced by FirebirdParser#sql_script.
    def enterSql_script(self, ctx:FirebirdParser.Sql_scriptContext):
        pass

    # Exit a parse tree produced by FirebirdParser#sql_script.
    def exitSql_script(self, ctx:FirebirdParser.Sql_scriptContext):
        pass


    # Enter a parse tree produced by FirebirdParser#unit_statement.
    def enterUnit_statement(self, ctx:FirebirdParser.Unit_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#unit_statement.
    def exitUnit_statement(self, ctx:FirebirdParser.Unit_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_diskgroup.
    def enterAlter_diskgroup(self, ctx:FirebirdParser.Alter_diskgroupContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_diskgroup.
    def exitAlter_diskgroup(self, ctx:FirebirdParser.Alter_diskgroupContext):
        pass


    # Enter a parse tree produced by FirebirdParser#add_disk_clause.
    def enterAdd_disk_clause(self, ctx:FirebirdParser.Add_disk_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#add_disk_clause.
    def exitAdd_disk_clause(self, ctx:FirebirdParser.Add_disk_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_disk_clause.
    def enterDrop_disk_clause(self, ctx:FirebirdParser.Drop_disk_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_disk_clause.
    def exitDrop_disk_clause(self, ctx:FirebirdParser.Drop_disk_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#resize_disk_clause.
    def enterResize_disk_clause(self, ctx:FirebirdParser.Resize_disk_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#resize_disk_clause.
    def exitResize_disk_clause(self, ctx:FirebirdParser.Resize_disk_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#replace_disk_clause.
    def enterReplace_disk_clause(self, ctx:FirebirdParser.Replace_disk_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#replace_disk_clause.
    def exitReplace_disk_clause(self, ctx:FirebirdParser.Replace_disk_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#wait_nowait.
    def enterWait_nowait(self, ctx:FirebirdParser.Wait_nowaitContext):
        pass

    # Exit a parse tree produced by FirebirdParser#wait_nowait.
    def exitWait_nowait(self, ctx:FirebirdParser.Wait_nowaitContext):
        pass


    # Enter a parse tree produced by FirebirdParser#rename_disk_clause.
    def enterRename_disk_clause(self, ctx:FirebirdParser.Rename_disk_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#rename_disk_clause.
    def exitRename_disk_clause(self, ctx:FirebirdParser.Rename_disk_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#disk_online_clause.
    def enterDisk_online_clause(self, ctx:FirebirdParser.Disk_online_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#disk_online_clause.
    def exitDisk_online_clause(self, ctx:FirebirdParser.Disk_online_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#disk_offline_clause.
    def enterDisk_offline_clause(self, ctx:FirebirdParser.Disk_offline_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#disk_offline_clause.
    def exitDisk_offline_clause(self, ctx:FirebirdParser.Disk_offline_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#timeout_clause.
    def enterTimeout_clause(self, ctx:FirebirdParser.Timeout_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#timeout_clause.
    def exitTimeout_clause(self, ctx:FirebirdParser.Timeout_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#rebalance_diskgroup_clause.
    def enterRebalance_diskgroup_clause(self, ctx:FirebirdParser.Rebalance_diskgroup_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#rebalance_diskgroup_clause.
    def exitRebalance_diskgroup_clause(self, ctx:FirebirdParser.Rebalance_diskgroup_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#phase.
    def enterPhase(self, ctx:FirebirdParser.PhaseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#phase.
    def exitPhase(self, ctx:FirebirdParser.PhaseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#check_diskgroup_clause.
    def enterCheck_diskgroup_clause(self, ctx:FirebirdParser.Check_diskgroup_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#check_diskgroup_clause.
    def exitCheck_diskgroup_clause(self, ctx:FirebirdParser.Check_diskgroup_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#diskgroup_template_clauses.
    def enterDiskgroup_template_clauses(self, ctx:FirebirdParser.Diskgroup_template_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#diskgroup_template_clauses.
    def exitDiskgroup_template_clauses(self, ctx:FirebirdParser.Diskgroup_template_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#qualified_template_clause.
    def enterQualified_template_clause(self, ctx:FirebirdParser.Qualified_template_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#qualified_template_clause.
    def exitQualified_template_clause(self, ctx:FirebirdParser.Qualified_template_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#redundancy_clause.
    def enterRedundancy_clause(self, ctx:FirebirdParser.Redundancy_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#redundancy_clause.
    def exitRedundancy_clause(self, ctx:FirebirdParser.Redundancy_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#striping_clause.
    def enterStriping_clause(self, ctx:FirebirdParser.Striping_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#striping_clause.
    def exitStriping_clause(self, ctx:FirebirdParser.Striping_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#force_noforce.
    def enterForce_noforce(self, ctx:FirebirdParser.Force_noforceContext):
        pass

    # Exit a parse tree produced by FirebirdParser#force_noforce.
    def exitForce_noforce(self, ctx:FirebirdParser.Force_noforceContext):
        pass


    # Enter a parse tree produced by FirebirdParser#diskgroup_directory_clauses.
    def enterDiskgroup_directory_clauses(self, ctx:FirebirdParser.Diskgroup_directory_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#diskgroup_directory_clauses.
    def exitDiskgroup_directory_clauses(self, ctx:FirebirdParser.Diskgroup_directory_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#dir_name.
    def enterDir_name(self, ctx:FirebirdParser.Dir_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#dir_name.
    def exitDir_name(self, ctx:FirebirdParser.Dir_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#diskgroup_alias_clauses.
    def enterDiskgroup_alias_clauses(self, ctx:FirebirdParser.Diskgroup_alias_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#diskgroup_alias_clauses.
    def exitDiskgroup_alias_clauses(self, ctx:FirebirdParser.Diskgroup_alias_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#diskgroup_volume_clauses.
    def enterDiskgroup_volume_clauses(self, ctx:FirebirdParser.Diskgroup_volume_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#diskgroup_volume_clauses.
    def exitDiskgroup_volume_clauses(self, ctx:FirebirdParser.Diskgroup_volume_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#add_volume_clause.
    def enterAdd_volume_clause(self, ctx:FirebirdParser.Add_volume_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#add_volume_clause.
    def exitAdd_volume_clause(self, ctx:FirebirdParser.Add_volume_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#modify_volume_clause.
    def enterModify_volume_clause(self, ctx:FirebirdParser.Modify_volume_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#modify_volume_clause.
    def exitModify_volume_clause(self, ctx:FirebirdParser.Modify_volume_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#diskgroup_attributes.
    def enterDiskgroup_attributes(self, ctx:FirebirdParser.Diskgroup_attributesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#diskgroup_attributes.
    def exitDiskgroup_attributes(self, ctx:FirebirdParser.Diskgroup_attributesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_diskgroup_file_clause.
    def enterDrop_diskgroup_file_clause(self, ctx:FirebirdParser.Drop_diskgroup_file_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_diskgroup_file_clause.
    def exitDrop_diskgroup_file_clause(self, ctx:FirebirdParser.Drop_diskgroup_file_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#convert_redundancy_clause.
    def enterConvert_redundancy_clause(self, ctx:FirebirdParser.Convert_redundancy_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#convert_redundancy_clause.
    def exitConvert_redundancy_clause(self, ctx:FirebirdParser.Convert_redundancy_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#usergroup_clauses.
    def enterUsergroup_clauses(self, ctx:FirebirdParser.Usergroup_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#usergroup_clauses.
    def exitUsergroup_clauses(self, ctx:FirebirdParser.Usergroup_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#user_clauses.
    def enterUser_clauses(self, ctx:FirebirdParser.User_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#user_clauses.
    def exitUser_clauses(self, ctx:FirebirdParser.User_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#file_permissions_clause.
    def enterFile_permissions_clause(self, ctx:FirebirdParser.File_permissions_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#file_permissions_clause.
    def exitFile_permissions_clause(self, ctx:FirebirdParser.File_permissions_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#file_owner_clause.
    def enterFile_owner_clause(self, ctx:FirebirdParser.File_owner_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#file_owner_clause.
    def exitFile_owner_clause(self, ctx:FirebirdParser.File_owner_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#scrub_clause.
    def enterScrub_clause(self, ctx:FirebirdParser.Scrub_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#scrub_clause.
    def exitScrub_clause(self, ctx:FirebirdParser.Scrub_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#quotagroup_clauses.
    def enterQuotagroup_clauses(self, ctx:FirebirdParser.Quotagroup_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#quotagroup_clauses.
    def exitQuotagroup_clauses(self, ctx:FirebirdParser.Quotagroup_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#property_name.
    def enterProperty_name(self, ctx:FirebirdParser.Property_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#property_name.
    def exitProperty_name(self, ctx:FirebirdParser.Property_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#property_value.
    def enterProperty_value(self, ctx:FirebirdParser.Property_valueContext):
        pass

    # Exit a parse tree produced by FirebirdParser#property_value.
    def exitProperty_value(self, ctx:FirebirdParser.Property_valueContext):
        pass


    # Enter a parse tree produced by FirebirdParser#filegroup_clauses.
    def enterFilegroup_clauses(self, ctx:FirebirdParser.Filegroup_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#filegroup_clauses.
    def exitFilegroup_clauses(self, ctx:FirebirdParser.Filegroup_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#add_filegroup_clause.
    def enterAdd_filegroup_clause(self, ctx:FirebirdParser.Add_filegroup_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#add_filegroup_clause.
    def exitAdd_filegroup_clause(self, ctx:FirebirdParser.Add_filegroup_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#modify_filegroup_clause.
    def enterModify_filegroup_clause(self, ctx:FirebirdParser.Modify_filegroup_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#modify_filegroup_clause.
    def exitModify_filegroup_clause(self, ctx:FirebirdParser.Modify_filegroup_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#move_to_filegroup_clause.
    def enterMove_to_filegroup_clause(self, ctx:FirebirdParser.Move_to_filegroup_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#move_to_filegroup_clause.
    def exitMove_to_filegroup_clause(self, ctx:FirebirdParser.Move_to_filegroup_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_filegroup_clause.
    def enterDrop_filegroup_clause(self, ctx:FirebirdParser.Drop_filegroup_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_filegroup_clause.
    def exitDrop_filegroup_clause(self, ctx:FirebirdParser.Drop_filegroup_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#quorum_regular.
    def enterQuorum_regular(self, ctx:FirebirdParser.Quorum_regularContext):
        pass

    # Exit a parse tree produced by FirebirdParser#quorum_regular.
    def exitQuorum_regular(self, ctx:FirebirdParser.Quorum_regularContext):
        pass


    # Enter a parse tree produced by FirebirdParser#undrop_disk_clause.
    def enterUndrop_disk_clause(self, ctx:FirebirdParser.Undrop_disk_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#undrop_disk_clause.
    def exitUndrop_disk_clause(self, ctx:FirebirdParser.Undrop_disk_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#diskgroup_availability.
    def enterDiskgroup_availability(self, ctx:FirebirdParser.Diskgroup_availabilityContext):
        pass

    # Exit a parse tree produced by FirebirdParser#diskgroup_availability.
    def exitDiskgroup_availability(self, ctx:FirebirdParser.Diskgroup_availabilityContext):
        pass


    # Enter a parse tree produced by FirebirdParser#enable_disable_volume.
    def enterEnable_disable_volume(self, ctx:FirebirdParser.Enable_disable_volumeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#enable_disable_volume.
    def exitEnable_disable_volume(self, ctx:FirebirdParser.Enable_disable_volumeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_function.
    def enterDrop_function(self, ctx:FirebirdParser.Drop_functionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_function.
    def exitDrop_function(self, ctx:FirebirdParser.Drop_functionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_flashback_archive.
    def enterAlter_flashback_archive(self, ctx:FirebirdParser.Alter_flashback_archiveContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_flashback_archive.
    def exitAlter_flashback_archive(self, ctx:FirebirdParser.Alter_flashback_archiveContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_hierarchy.
    def enterAlter_hierarchy(self, ctx:FirebirdParser.Alter_hierarchyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_hierarchy.
    def exitAlter_hierarchy(self, ctx:FirebirdParser.Alter_hierarchyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_function.
    def enterAlter_function(self, ctx:FirebirdParser.Alter_functionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_function.
    def exitAlter_function(self, ctx:FirebirdParser.Alter_functionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_java.
    def enterAlter_java(self, ctx:FirebirdParser.Alter_javaContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_java.
    def exitAlter_java(self, ctx:FirebirdParser.Alter_javaContext):
        pass


    # Enter a parse tree produced by FirebirdParser#match_string.
    def enterMatch_string(self, ctx:FirebirdParser.Match_stringContext):
        pass

    # Exit a parse tree produced by FirebirdParser#match_string.
    def exitMatch_string(self, ctx:FirebirdParser.Match_stringContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_function_body.
    def enterCreate_function_body(self, ctx:FirebirdParser.Create_function_bodyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_function_body.
    def exitCreate_function_body(self, ctx:FirebirdParser.Create_function_bodyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#sql_macro_body.
    def enterSql_macro_body(self, ctx:FirebirdParser.Sql_macro_bodyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#sql_macro_body.
    def exitSql_macro_body(self, ctx:FirebirdParser.Sql_macro_bodyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#parallel_enable_clause.
    def enterParallel_enable_clause(self, ctx:FirebirdParser.Parallel_enable_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#parallel_enable_clause.
    def exitParallel_enable_clause(self, ctx:FirebirdParser.Parallel_enable_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#partition_by_clause.
    def enterPartition_by_clause(self, ctx:FirebirdParser.Partition_by_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#partition_by_clause.
    def exitPartition_by_clause(self, ctx:FirebirdParser.Partition_by_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#result_cache_clause.
    def enterResult_cache_clause(self, ctx:FirebirdParser.Result_cache_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#result_cache_clause.
    def exitResult_cache_clause(self, ctx:FirebirdParser.Result_cache_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#accessible_by_clause.
    def enterAccessible_by_clause(self, ctx:FirebirdParser.Accessible_by_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#accessible_by_clause.
    def exitAccessible_by_clause(self, ctx:FirebirdParser.Accessible_by_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#default_collation_clause.
    def enterDefault_collation_clause(self, ctx:FirebirdParser.Default_collation_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#default_collation_clause.
    def exitDefault_collation_clause(self, ctx:FirebirdParser.Default_collation_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#aggregate_clause.
    def enterAggregate_clause(self, ctx:FirebirdParser.Aggregate_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#aggregate_clause.
    def exitAggregate_clause(self, ctx:FirebirdParser.Aggregate_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#pipelined_using_clause.
    def enterPipelined_using_clause(self, ctx:FirebirdParser.Pipelined_using_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#pipelined_using_clause.
    def exitPipelined_using_clause(self, ctx:FirebirdParser.Pipelined_using_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#accessor.
    def enterAccessor(self, ctx:FirebirdParser.AccessorContext):
        pass

    # Exit a parse tree produced by FirebirdParser#accessor.
    def exitAccessor(self, ctx:FirebirdParser.AccessorContext):
        pass


    # Enter a parse tree produced by FirebirdParser#relies_on_part.
    def enterRelies_on_part(self, ctx:FirebirdParser.Relies_on_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#relies_on_part.
    def exitRelies_on_part(self, ctx:FirebirdParser.Relies_on_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#streaming_clause.
    def enterStreaming_clause(self, ctx:FirebirdParser.Streaming_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#streaming_clause.
    def exitStreaming_clause(self, ctx:FirebirdParser.Streaming_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_outline.
    def enterAlter_outline(self, ctx:FirebirdParser.Alter_outlineContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_outline.
    def exitAlter_outline(self, ctx:FirebirdParser.Alter_outlineContext):
        pass


    # Enter a parse tree produced by FirebirdParser#outline_options.
    def enterOutline_options(self, ctx:FirebirdParser.Outline_optionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#outline_options.
    def exitOutline_options(self, ctx:FirebirdParser.Outline_optionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_lockdown_profile.
    def enterAlter_lockdown_profile(self, ctx:FirebirdParser.Alter_lockdown_profileContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_lockdown_profile.
    def exitAlter_lockdown_profile(self, ctx:FirebirdParser.Alter_lockdown_profileContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lockdown_feature.
    def enterLockdown_feature(self, ctx:FirebirdParser.Lockdown_featureContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lockdown_feature.
    def exitLockdown_feature(self, ctx:FirebirdParser.Lockdown_featureContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lockdown_options.
    def enterLockdown_options(self, ctx:FirebirdParser.Lockdown_optionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lockdown_options.
    def exitLockdown_options(self, ctx:FirebirdParser.Lockdown_optionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lockdown_statements.
    def enterLockdown_statements(self, ctx:FirebirdParser.Lockdown_statementsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lockdown_statements.
    def exitLockdown_statements(self, ctx:FirebirdParser.Lockdown_statementsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#statement_clauses.
    def enterStatement_clauses(self, ctx:FirebirdParser.Statement_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#statement_clauses.
    def exitStatement_clauses(self, ctx:FirebirdParser.Statement_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#clause_options.
    def enterClause_options(self, ctx:FirebirdParser.Clause_optionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#clause_options.
    def exitClause_options(self, ctx:FirebirdParser.Clause_optionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#option_values.
    def enterOption_values(self, ctx:FirebirdParser.Option_valuesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#option_values.
    def exitOption_values(self, ctx:FirebirdParser.Option_valuesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#string_list.
    def enterString_list(self, ctx:FirebirdParser.String_listContext):
        pass

    # Exit a parse tree produced by FirebirdParser#string_list.
    def exitString_list(self, ctx:FirebirdParser.String_listContext):
        pass


    # Enter a parse tree produced by FirebirdParser#disable_enable.
    def enterDisable_enable(self, ctx:FirebirdParser.Disable_enableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#disable_enable.
    def exitDisable_enable(self, ctx:FirebirdParser.Disable_enableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_lockdown_profile.
    def enterDrop_lockdown_profile(self, ctx:FirebirdParser.Drop_lockdown_profileContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_lockdown_profile.
    def exitDrop_lockdown_profile(self, ctx:FirebirdParser.Drop_lockdown_profileContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_package.
    def enterDrop_package(self, ctx:FirebirdParser.Drop_packageContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_package.
    def exitDrop_package(self, ctx:FirebirdParser.Drop_packageContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_package.
    def enterAlter_package(self, ctx:FirebirdParser.Alter_packageContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_package.
    def exitAlter_package(self, ctx:FirebirdParser.Alter_packageContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_package.
    def enterCreate_package(self, ctx:FirebirdParser.Create_packageContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_package.
    def exitCreate_package(self, ctx:FirebirdParser.Create_packageContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_package_body.
    def enterCreate_package_body(self, ctx:FirebirdParser.Create_package_bodyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_package_body.
    def exitCreate_package_body(self, ctx:FirebirdParser.Create_package_bodyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#package_obj_spec.
    def enterPackage_obj_spec(self, ctx:FirebirdParser.Package_obj_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#package_obj_spec.
    def exitPackage_obj_spec(self, ctx:FirebirdParser.Package_obj_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#procedure_spec.
    def enterProcedure_spec(self, ctx:FirebirdParser.Procedure_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#procedure_spec.
    def exitProcedure_spec(self, ctx:FirebirdParser.Procedure_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#function_spec.
    def enterFunction_spec(self, ctx:FirebirdParser.Function_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#function_spec.
    def exitFunction_spec(self, ctx:FirebirdParser.Function_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#package_obj_body.
    def enterPackage_obj_body(self, ctx:FirebirdParser.Package_obj_bodyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#package_obj_body.
    def exitPackage_obj_body(self, ctx:FirebirdParser.Package_obj_bodyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_pmem_filestore.
    def enterAlter_pmem_filestore(self, ctx:FirebirdParser.Alter_pmem_filestoreContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_pmem_filestore.
    def exitAlter_pmem_filestore(self, ctx:FirebirdParser.Alter_pmem_filestoreContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_pmem_filestore.
    def enterDrop_pmem_filestore(self, ctx:FirebirdParser.Drop_pmem_filestoreContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_pmem_filestore.
    def exitDrop_pmem_filestore(self, ctx:FirebirdParser.Drop_pmem_filestoreContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_procedure.
    def enterDrop_procedure(self, ctx:FirebirdParser.Drop_procedureContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_procedure.
    def exitDrop_procedure(self, ctx:FirebirdParser.Drop_procedureContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_procedure.
    def enterAlter_procedure(self, ctx:FirebirdParser.Alter_procedureContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_procedure.
    def exitAlter_procedure(self, ctx:FirebirdParser.Alter_procedureContext):
        pass


    # Enter a parse tree produced by FirebirdParser#function_body.
    def enterFunction_body(self, ctx:FirebirdParser.Function_bodyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#function_body.
    def exitFunction_body(self, ctx:FirebirdParser.Function_bodyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#procedure_body.
    def enterProcedure_body(self, ctx:FirebirdParser.Procedure_bodyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#procedure_body.
    def exitProcedure_body(self, ctx:FirebirdParser.Procedure_bodyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_procedure_body.
    def enterCreate_procedure_body(self, ctx:FirebirdParser.Create_procedure_bodyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_procedure_body.
    def exitCreate_procedure_body(self, ctx:FirebirdParser.Create_procedure_bodyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_resource_cost.
    def enterAlter_resource_cost(self, ctx:FirebirdParser.Alter_resource_costContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_resource_cost.
    def exitAlter_resource_cost(self, ctx:FirebirdParser.Alter_resource_costContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_outline.
    def enterDrop_outline(self, ctx:FirebirdParser.Drop_outlineContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_outline.
    def exitDrop_outline(self, ctx:FirebirdParser.Drop_outlineContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_rollback_segment.
    def enterAlter_rollback_segment(self, ctx:FirebirdParser.Alter_rollback_segmentContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_rollback_segment.
    def exitAlter_rollback_segment(self, ctx:FirebirdParser.Alter_rollback_segmentContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_restore_point.
    def enterDrop_restore_point(self, ctx:FirebirdParser.Drop_restore_pointContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_restore_point.
    def exitDrop_restore_point(self, ctx:FirebirdParser.Drop_restore_pointContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_rollback_segment.
    def enterDrop_rollback_segment(self, ctx:FirebirdParser.Drop_rollback_segmentContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_rollback_segment.
    def exitDrop_rollback_segment(self, ctx:FirebirdParser.Drop_rollback_segmentContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_role.
    def enterDrop_role(self, ctx:FirebirdParser.Drop_roleContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_role.
    def exitDrop_role(self, ctx:FirebirdParser.Drop_roleContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_pmem_filestore.
    def enterCreate_pmem_filestore(self, ctx:FirebirdParser.Create_pmem_filestoreContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_pmem_filestore.
    def exitCreate_pmem_filestore(self, ctx:FirebirdParser.Create_pmem_filestoreContext):
        pass


    # Enter a parse tree produced by FirebirdParser#pmem_filestore_options.
    def enterPmem_filestore_options(self, ctx:FirebirdParser.Pmem_filestore_optionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#pmem_filestore_options.
    def exitPmem_filestore_options(self, ctx:FirebirdParser.Pmem_filestore_optionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#file_path.
    def enterFile_path(self, ctx:FirebirdParser.File_pathContext):
        pass

    # Exit a parse tree produced by FirebirdParser#file_path.
    def exitFile_path(self, ctx:FirebirdParser.File_pathContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_rollback_segment.
    def enterCreate_rollback_segment(self, ctx:FirebirdParser.Create_rollback_segmentContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_rollback_segment.
    def exitCreate_rollback_segment(self, ctx:FirebirdParser.Create_rollback_segmentContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_trigger.
    def enterDrop_trigger(self, ctx:FirebirdParser.Drop_triggerContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_trigger.
    def exitDrop_trigger(self, ctx:FirebirdParser.Drop_triggerContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_trigger.
    def enterAlter_trigger(self, ctx:FirebirdParser.Alter_triggerContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_trigger.
    def exitAlter_trigger(self, ctx:FirebirdParser.Alter_triggerContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_trigger.
    def enterCreate_trigger(self, ctx:FirebirdParser.Create_triggerContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_trigger.
    def exitCreate_trigger(self, ctx:FirebirdParser.Create_triggerContext):
        pass


    # Enter a parse tree produced by FirebirdParser#trigger_follows_clause.
    def enterTrigger_follows_clause(self, ctx:FirebirdParser.Trigger_follows_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#trigger_follows_clause.
    def exitTrigger_follows_clause(self, ctx:FirebirdParser.Trigger_follows_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#trigger_when_clause.
    def enterTrigger_when_clause(self, ctx:FirebirdParser.Trigger_when_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#trigger_when_clause.
    def exitTrigger_when_clause(self, ctx:FirebirdParser.Trigger_when_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#simple_dml_trigger.
    def enterSimple_dml_trigger(self, ctx:FirebirdParser.Simple_dml_triggerContext):
        pass

    # Exit a parse tree produced by FirebirdParser#simple_dml_trigger.
    def exitSimple_dml_trigger(self, ctx:FirebirdParser.Simple_dml_triggerContext):
        pass


    # Enter a parse tree produced by FirebirdParser#for_each_row.
    def enterFor_each_row(self, ctx:FirebirdParser.For_each_rowContext):
        pass

    # Exit a parse tree produced by FirebirdParser#for_each_row.
    def exitFor_each_row(self, ctx:FirebirdParser.For_each_rowContext):
        pass


    # Enter a parse tree produced by FirebirdParser#compound_dml_trigger.
    def enterCompound_dml_trigger(self, ctx:FirebirdParser.Compound_dml_triggerContext):
        pass

    # Exit a parse tree produced by FirebirdParser#compound_dml_trigger.
    def exitCompound_dml_trigger(self, ctx:FirebirdParser.Compound_dml_triggerContext):
        pass


    # Enter a parse tree produced by FirebirdParser#non_dml_trigger.
    def enterNon_dml_trigger(self, ctx:FirebirdParser.Non_dml_triggerContext):
        pass

    # Exit a parse tree produced by FirebirdParser#non_dml_trigger.
    def exitNon_dml_trigger(self, ctx:FirebirdParser.Non_dml_triggerContext):
        pass


    # Enter a parse tree produced by FirebirdParser#trigger_body.
    def enterTrigger_body(self, ctx:FirebirdParser.Trigger_bodyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#trigger_body.
    def exitTrigger_body(self, ctx:FirebirdParser.Trigger_bodyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#compound_trigger_block.
    def enterCompound_trigger_block(self, ctx:FirebirdParser.Compound_trigger_blockContext):
        pass

    # Exit a parse tree produced by FirebirdParser#compound_trigger_block.
    def exitCompound_trigger_block(self, ctx:FirebirdParser.Compound_trigger_blockContext):
        pass


    # Enter a parse tree produced by FirebirdParser#timing_point_section.
    def enterTiming_point_section(self, ctx:FirebirdParser.Timing_point_sectionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#timing_point_section.
    def exitTiming_point_section(self, ctx:FirebirdParser.Timing_point_sectionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#non_dml_event.
    def enterNon_dml_event(self, ctx:FirebirdParser.Non_dml_eventContext):
        pass

    # Exit a parse tree produced by FirebirdParser#non_dml_event.
    def exitNon_dml_event(self, ctx:FirebirdParser.Non_dml_eventContext):
        pass


    # Enter a parse tree produced by FirebirdParser#dml_event_clause.
    def enterDml_event_clause(self, ctx:FirebirdParser.Dml_event_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#dml_event_clause.
    def exitDml_event_clause(self, ctx:FirebirdParser.Dml_event_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#dml_event_element.
    def enterDml_event_element(self, ctx:FirebirdParser.Dml_event_elementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#dml_event_element.
    def exitDml_event_element(self, ctx:FirebirdParser.Dml_event_elementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#dml_event_nested_clause.
    def enterDml_event_nested_clause(self, ctx:FirebirdParser.Dml_event_nested_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#dml_event_nested_clause.
    def exitDml_event_nested_clause(self, ctx:FirebirdParser.Dml_event_nested_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#referencing_clause.
    def enterReferencing_clause(self, ctx:FirebirdParser.Referencing_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#referencing_clause.
    def exitReferencing_clause(self, ctx:FirebirdParser.Referencing_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#referencing_element.
    def enterReferencing_element(self, ctx:FirebirdParser.Referencing_elementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#referencing_element.
    def exitReferencing_element(self, ctx:FirebirdParser.Referencing_elementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_type.
    def enterDrop_type(self, ctx:FirebirdParser.Drop_typeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_type.
    def exitDrop_type(self, ctx:FirebirdParser.Drop_typeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_type.
    def enterAlter_type(self, ctx:FirebirdParser.Alter_typeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_type.
    def exitAlter_type(self, ctx:FirebirdParser.Alter_typeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#compile_type_clause.
    def enterCompile_type_clause(self, ctx:FirebirdParser.Compile_type_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#compile_type_clause.
    def exitCompile_type_clause(self, ctx:FirebirdParser.Compile_type_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#replace_type_clause.
    def enterReplace_type_clause(self, ctx:FirebirdParser.Replace_type_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#replace_type_clause.
    def exitReplace_type_clause(self, ctx:FirebirdParser.Replace_type_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_method_spec.
    def enterAlter_method_spec(self, ctx:FirebirdParser.Alter_method_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_method_spec.
    def exitAlter_method_spec(self, ctx:FirebirdParser.Alter_method_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_method_element.
    def enterAlter_method_element(self, ctx:FirebirdParser.Alter_method_elementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_method_element.
    def exitAlter_method_element(self, ctx:FirebirdParser.Alter_method_elementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_collection_clauses.
    def enterAlter_collection_clauses(self, ctx:FirebirdParser.Alter_collection_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_collection_clauses.
    def exitAlter_collection_clauses(self, ctx:FirebirdParser.Alter_collection_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#dependent_handling_clause.
    def enterDependent_handling_clause(self, ctx:FirebirdParser.Dependent_handling_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#dependent_handling_clause.
    def exitDependent_handling_clause(self, ctx:FirebirdParser.Dependent_handling_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#dependent_exceptions_part.
    def enterDependent_exceptions_part(self, ctx:FirebirdParser.Dependent_exceptions_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#dependent_exceptions_part.
    def exitDependent_exceptions_part(self, ctx:FirebirdParser.Dependent_exceptions_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_type.
    def enterCreate_type(self, ctx:FirebirdParser.Create_typeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_type.
    def exitCreate_type(self, ctx:FirebirdParser.Create_typeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#type_definition.
    def enterType_definition(self, ctx:FirebirdParser.Type_definitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#type_definition.
    def exitType_definition(self, ctx:FirebirdParser.Type_definitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#object_type_def.
    def enterObject_type_def(self, ctx:FirebirdParser.Object_type_defContext):
        pass

    # Exit a parse tree produced by FirebirdParser#object_type_def.
    def exitObject_type_def(self, ctx:FirebirdParser.Object_type_defContext):
        pass


    # Enter a parse tree produced by FirebirdParser#object_as_part.
    def enterObject_as_part(self, ctx:FirebirdParser.Object_as_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#object_as_part.
    def exitObject_as_part(self, ctx:FirebirdParser.Object_as_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#object_under_part.
    def enterObject_under_part(self, ctx:FirebirdParser.Object_under_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#object_under_part.
    def exitObject_under_part(self, ctx:FirebirdParser.Object_under_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#nested_table_type_def.
    def enterNested_table_type_def(self, ctx:FirebirdParser.Nested_table_type_defContext):
        pass

    # Exit a parse tree produced by FirebirdParser#nested_table_type_def.
    def exitNested_table_type_def(self, ctx:FirebirdParser.Nested_table_type_defContext):
        pass


    # Enter a parse tree produced by FirebirdParser#sqlj_object_type.
    def enterSqlj_object_type(self, ctx:FirebirdParser.Sqlj_object_typeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#sqlj_object_type.
    def exitSqlj_object_type(self, ctx:FirebirdParser.Sqlj_object_typeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#type_body.
    def enterType_body(self, ctx:FirebirdParser.Type_bodyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#type_body.
    def exitType_body(self, ctx:FirebirdParser.Type_bodyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#type_body_elements.
    def enterType_body_elements(self, ctx:FirebirdParser.Type_body_elementsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#type_body_elements.
    def exitType_body_elements(self, ctx:FirebirdParser.Type_body_elementsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#map_order_func_declaration.
    def enterMap_order_func_declaration(self, ctx:FirebirdParser.Map_order_func_declarationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#map_order_func_declaration.
    def exitMap_order_func_declaration(self, ctx:FirebirdParser.Map_order_func_declarationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#subprog_decl_in_type.
    def enterSubprog_decl_in_type(self, ctx:FirebirdParser.Subprog_decl_in_typeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#subprog_decl_in_type.
    def exitSubprog_decl_in_type(self, ctx:FirebirdParser.Subprog_decl_in_typeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#proc_decl_in_type.
    def enterProc_decl_in_type(self, ctx:FirebirdParser.Proc_decl_in_typeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#proc_decl_in_type.
    def exitProc_decl_in_type(self, ctx:FirebirdParser.Proc_decl_in_typeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#func_decl_in_type.
    def enterFunc_decl_in_type(self, ctx:FirebirdParser.Func_decl_in_typeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#func_decl_in_type.
    def exitFunc_decl_in_type(self, ctx:FirebirdParser.Func_decl_in_typeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#constructor_declaration.
    def enterConstructor_declaration(self, ctx:FirebirdParser.Constructor_declarationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#constructor_declaration.
    def exitConstructor_declaration(self, ctx:FirebirdParser.Constructor_declarationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#modifier_clause.
    def enterModifier_clause(self, ctx:FirebirdParser.Modifier_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#modifier_clause.
    def exitModifier_clause(self, ctx:FirebirdParser.Modifier_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#object_member_spec.
    def enterObject_member_spec(self, ctx:FirebirdParser.Object_member_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#object_member_spec.
    def exitObject_member_spec(self, ctx:FirebirdParser.Object_member_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#sqlj_object_type_attr.
    def enterSqlj_object_type_attr(self, ctx:FirebirdParser.Sqlj_object_type_attrContext):
        pass

    # Exit a parse tree produced by FirebirdParser#sqlj_object_type_attr.
    def exitSqlj_object_type_attr(self, ctx:FirebirdParser.Sqlj_object_type_attrContext):
        pass


    # Enter a parse tree produced by FirebirdParser#element_spec.
    def enterElement_spec(self, ctx:FirebirdParser.Element_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#element_spec.
    def exitElement_spec(self, ctx:FirebirdParser.Element_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#element_spec_options.
    def enterElement_spec_options(self, ctx:FirebirdParser.Element_spec_optionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#element_spec_options.
    def exitElement_spec_options(self, ctx:FirebirdParser.Element_spec_optionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#subprogram_spec.
    def enterSubprogram_spec(self, ctx:FirebirdParser.Subprogram_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#subprogram_spec.
    def exitSubprogram_spec(self, ctx:FirebirdParser.Subprogram_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#overriding_subprogram_spec.
    def enterOverriding_subprogram_spec(self, ctx:FirebirdParser.Overriding_subprogram_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#overriding_subprogram_spec.
    def exitOverriding_subprogram_spec(self, ctx:FirebirdParser.Overriding_subprogram_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#overriding_function_spec.
    def enterOverriding_function_spec(self, ctx:FirebirdParser.Overriding_function_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#overriding_function_spec.
    def exitOverriding_function_spec(self, ctx:FirebirdParser.Overriding_function_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#overriding_procedure_spec.
    def enterOverriding_procedure_spec(self, ctx:FirebirdParser.Overriding_procedure_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#overriding_procedure_spec.
    def exitOverriding_procedure_spec(self, ctx:FirebirdParser.Overriding_procedure_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#type_procedure_spec.
    def enterType_procedure_spec(self, ctx:FirebirdParser.Type_procedure_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#type_procedure_spec.
    def exitType_procedure_spec(self, ctx:FirebirdParser.Type_procedure_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#type_function_spec.
    def enterType_function_spec(self, ctx:FirebirdParser.Type_function_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#type_function_spec.
    def exitType_function_spec(self, ctx:FirebirdParser.Type_function_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#constructor_spec.
    def enterConstructor_spec(self, ctx:FirebirdParser.Constructor_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#constructor_spec.
    def exitConstructor_spec(self, ctx:FirebirdParser.Constructor_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#map_order_function_spec.
    def enterMap_order_function_spec(self, ctx:FirebirdParser.Map_order_function_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#map_order_function_spec.
    def exitMap_order_function_spec(self, ctx:FirebirdParser.Map_order_function_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#pragma_clause.
    def enterPragma_clause(self, ctx:FirebirdParser.Pragma_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#pragma_clause.
    def exitPragma_clause(self, ctx:FirebirdParser.Pragma_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#pragma_elements.
    def enterPragma_elements(self, ctx:FirebirdParser.Pragma_elementsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#pragma_elements.
    def exitPragma_elements(self, ctx:FirebirdParser.Pragma_elementsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#type_elements_parameter.
    def enterType_elements_parameter(self, ctx:FirebirdParser.Type_elements_parameterContext):
        pass

    # Exit a parse tree produced by FirebirdParser#type_elements_parameter.
    def exitType_elements_parameter(self, ctx:FirebirdParser.Type_elements_parameterContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_sequence.
    def enterDrop_sequence(self, ctx:FirebirdParser.Drop_sequenceContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_sequence.
    def exitDrop_sequence(self, ctx:FirebirdParser.Drop_sequenceContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_sequence.
    def enterAlter_sequence(self, ctx:FirebirdParser.Alter_sequenceContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_sequence.
    def exitAlter_sequence(self, ctx:FirebirdParser.Alter_sequenceContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_session.
    def enterAlter_session(self, ctx:FirebirdParser.Alter_sessionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_session.
    def exitAlter_session(self, ctx:FirebirdParser.Alter_sessionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_session_set_clause.
    def enterAlter_session_set_clause(self, ctx:FirebirdParser.Alter_session_set_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_session_set_clause.
    def exitAlter_session_set_clause(self, ctx:FirebirdParser.Alter_session_set_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_sequence.
    def enterCreate_sequence(self, ctx:FirebirdParser.Create_sequenceContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_sequence.
    def exitCreate_sequence(self, ctx:FirebirdParser.Create_sequenceContext):
        pass


    # Enter a parse tree produced by FirebirdParser#sequence_spec.
    def enterSequence_spec(self, ctx:FirebirdParser.Sequence_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#sequence_spec.
    def exitSequence_spec(self, ctx:FirebirdParser.Sequence_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#sequence_start_clause.
    def enterSequence_start_clause(self, ctx:FirebirdParser.Sequence_start_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#sequence_start_clause.
    def exitSequence_start_clause(self, ctx:FirebirdParser.Sequence_start_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_analytic_view.
    def enterCreate_analytic_view(self, ctx:FirebirdParser.Create_analytic_viewContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_analytic_view.
    def exitCreate_analytic_view(self, ctx:FirebirdParser.Create_analytic_viewContext):
        pass


    # Enter a parse tree produced by FirebirdParser#classification_clause.
    def enterClassification_clause(self, ctx:FirebirdParser.Classification_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#classification_clause.
    def exitClassification_clause(self, ctx:FirebirdParser.Classification_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#caption_clause.
    def enterCaption_clause(self, ctx:FirebirdParser.Caption_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#caption_clause.
    def exitCaption_clause(self, ctx:FirebirdParser.Caption_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#description_clause.
    def enterDescription_clause(self, ctx:FirebirdParser.Description_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#description_clause.
    def exitDescription_clause(self, ctx:FirebirdParser.Description_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#classification_item.
    def enterClassification_item(self, ctx:FirebirdParser.Classification_itemContext):
        pass

    # Exit a parse tree produced by FirebirdParser#classification_item.
    def exitClassification_item(self, ctx:FirebirdParser.Classification_itemContext):
        pass


    # Enter a parse tree produced by FirebirdParser#language.
    def enterLanguage(self, ctx:FirebirdParser.LanguageContext):
        pass

    # Exit a parse tree produced by FirebirdParser#language.
    def exitLanguage(self, ctx:FirebirdParser.LanguageContext):
        pass


    # Enter a parse tree produced by FirebirdParser#cav_using_clause.
    def enterCav_using_clause(self, ctx:FirebirdParser.Cav_using_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#cav_using_clause.
    def exitCav_using_clause(self, ctx:FirebirdParser.Cav_using_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#dim_by_clause.
    def enterDim_by_clause(self, ctx:FirebirdParser.Dim_by_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#dim_by_clause.
    def exitDim_by_clause(self, ctx:FirebirdParser.Dim_by_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#dim_key.
    def enterDim_key(self, ctx:FirebirdParser.Dim_keyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#dim_key.
    def exitDim_key(self, ctx:FirebirdParser.Dim_keyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#dim_ref.
    def enterDim_ref(self, ctx:FirebirdParser.Dim_refContext):
        pass

    # Exit a parse tree produced by FirebirdParser#dim_ref.
    def exitDim_ref(self, ctx:FirebirdParser.Dim_refContext):
        pass


    # Enter a parse tree produced by FirebirdParser#hier_ref.
    def enterHier_ref(self, ctx:FirebirdParser.Hier_refContext):
        pass

    # Exit a parse tree produced by FirebirdParser#hier_ref.
    def exitHier_ref(self, ctx:FirebirdParser.Hier_refContext):
        pass


    # Enter a parse tree produced by FirebirdParser#measures_clause.
    def enterMeasures_clause(self, ctx:FirebirdParser.Measures_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#measures_clause.
    def exitMeasures_clause(self, ctx:FirebirdParser.Measures_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#av_measure.
    def enterAv_measure(self, ctx:FirebirdParser.Av_measureContext):
        pass

    # Exit a parse tree produced by FirebirdParser#av_measure.
    def exitAv_measure(self, ctx:FirebirdParser.Av_measureContext):
        pass


    # Enter a parse tree produced by FirebirdParser#base_meas_clause.
    def enterBase_meas_clause(self, ctx:FirebirdParser.Base_meas_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#base_meas_clause.
    def exitBase_meas_clause(self, ctx:FirebirdParser.Base_meas_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#meas_aggregate_clause.
    def enterMeas_aggregate_clause(self, ctx:FirebirdParser.Meas_aggregate_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#meas_aggregate_clause.
    def exitMeas_aggregate_clause(self, ctx:FirebirdParser.Meas_aggregate_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#calc_meas_clause.
    def enterCalc_meas_clause(self, ctx:FirebirdParser.Calc_meas_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#calc_meas_clause.
    def exitCalc_meas_clause(self, ctx:FirebirdParser.Calc_meas_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#default_measure_clause.
    def enterDefault_measure_clause(self, ctx:FirebirdParser.Default_measure_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#default_measure_clause.
    def exitDefault_measure_clause(self, ctx:FirebirdParser.Default_measure_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#default_aggregate_clause.
    def enterDefault_aggregate_clause(self, ctx:FirebirdParser.Default_aggregate_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#default_aggregate_clause.
    def exitDefault_aggregate_clause(self, ctx:FirebirdParser.Default_aggregate_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#cache_clause.
    def enterCache_clause(self, ctx:FirebirdParser.Cache_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#cache_clause.
    def exitCache_clause(self, ctx:FirebirdParser.Cache_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#cache_specification.
    def enterCache_specification(self, ctx:FirebirdParser.Cache_specificationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#cache_specification.
    def exitCache_specification(self, ctx:FirebirdParser.Cache_specificationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#levels_clause.
    def enterLevels_clause(self, ctx:FirebirdParser.Levels_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#levels_clause.
    def exitLevels_clause(self, ctx:FirebirdParser.Levels_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#level_specification.
    def enterLevel_specification(self, ctx:FirebirdParser.Level_specificationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#level_specification.
    def exitLevel_specification(self, ctx:FirebirdParser.Level_specificationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#level_group_type.
    def enterLevel_group_type(self, ctx:FirebirdParser.Level_group_typeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#level_group_type.
    def exitLevel_group_type(self, ctx:FirebirdParser.Level_group_typeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#fact_columns_clause.
    def enterFact_columns_clause(self, ctx:FirebirdParser.Fact_columns_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#fact_columns_clause.
    def exitFact_columns_clause(self, ctx:FirebirdParser.Fact_columns_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#qry_transform_clause.
    def enterQry_transform_clause(self, ctx:FirebirdParser.Qry_transform_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#qry_transform_clause.
    def exitQry_transform_clause(self, ctx:FirebirdParser.Qry_transform_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_attribute_dimension.
    def enterCreate_attribute_dimension(self, ctx:FirebirdParser.Create_attribute_dimensionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_attribute_dimension.
    def exitCreate_attribute_dimension(self, ctx:FirebirdParser.Create_attribute_dimensionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#ad_using_clause.
    def enterAd_using_clause(self, ctx:FirebirdParser.Ad_using_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#ad_using_clause.
    def exitAd_using_clause(self, ctx:FirebirdParser.Ad_using_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#source_clause.
    def enterSource_clause(self, ctx:FirebirdParser.Source_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#source_clause.
    def exitSource_clause(self, ctx:FirebirdParser.Source_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#join_path_clause.
    def enterJoin_path_clause(self, ctx:FirebirdParser.Join_path_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#join_path_clause.
    def exitJoin_path_clause(self, ctx:FirebirdParser.Join_path_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#join_condition.
    def enterJoin_condition(self, ctx:FirebirdParser.Join_conditionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#join_condition.
    def exitJoin_condition(self, ctx:FirebirdParser.Join_conditionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#join_condition_item.
    def enterJoin_condition_item(self, ctx:FirebirdParser.Join_condition_itemContext):
        pass

    # Exit a parse tree produced by FirebirdParser#join_condition_item.
    def exitJoin_condition_item(self, ctx:FirebirdParser.Join_condition_itemContext):
        pass


    # Enter a parse tree produced by FirebirdParser#attributes_clause.
    def enterAttributes_clause(self, ctx:FirebirdParser.Attributes_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#attributes_clause.
    def exitAttributes_clause(self, ctx:FirebirdParser.Attributes_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#ad_attributes_clause.
    def enterAd_attributes_clause(self, ctx:FirebirdParser.Ad_attributes_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#ad_attributes_clause.
    def exitAd_attributes_clause(self, ctx:FirebirdParser.Ad_attributes_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#ad_level_clause.
    def enterAd_level_clause(self, ctx:FirebirdParser.Ad_level_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#ad_level_clause.
    def exitAd_level_clause(self, ctx:FirebirdParser.Ad_level_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#key_clause.
    def enterKey_clause(self, ctx:FirebirdParser.Key_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#key_clause.
    def exitKey_clause(self, ctx:FirebirdParser.Key_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alternate_key_clause.
    def enterAlternate_key_clause(self, ctx:FirebirdParser.Alternate_key_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alternate_key_clause.
    def exitAlternate_key_clause(self, ctx:FirebirdParser.Alternate_key_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#dim_order_clause.
    def enterDim_order_clause(self, ctx:FirebirdParser.Dim_order_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#dim_order_clause.
    def exitDim_order_clause(self, ctx:FirebirdParser.Dim_order_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#all_clause.
    def enterAll_clause(self, ctx:FirebirdParser.All_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#all_clause.
    def exitAll_clause(self, ctx:FirebirdParser.All_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_audit_policy.
    def enterCreate_audit_policy(self, ctx:FirebirdParser.Create_audit_policyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_audit_policy.
    def exitCreate_audit_policy(self, ctx:FirebirdParser.Create_audit_policyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#privilege_audit_clause.
    def enterPrivilege_audit_clause(self, ctx:FirebirdParser.Privilege_audit_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#privilege_audit_clause.
    def exitPrivilege_audit_clause(self, ctx:FirebirdParser.Privilege_audit_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#action_audit_clause.
    def enterAction_audit_clause(self, ctx:FirebirdParser.Action_audit_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#action_audit_clause.
    def exitAction_audit_clause(self, ctx:FirebirdParser.Action_audit_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#system_actions.
    def enterSystem_actions(self, ctx:FirebirdParser.System_actionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#system_actions.
    def exitSystem_actions(self, ctx:FirebirdParser.System_actionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#standard_actions.
    def enterStandard_actions(self, ctx:FirebirdParser.Standard_actionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#standard_actions.
    def exitStandard_actions(self, ctx:FirebirdParser.Standard_actionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#actions_clause.
    def enterActions_clause(self, ctx:FirebirdParser.Actions_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#actions_clause.
    def exitActions_clause(self, ctx:FirebirdParser.Actions_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#object_action.
    def enterObject_action(self, ctx:FirebirdParser.Object_actionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#object_action.
    def exitObject_action(self, ctx:FirebirdParser.Object_actionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#system_action.
    def enterSystem_action(self, ctx:FirebirdParser.System_actionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#system_action.
    def exitSystem_action(self, ctx:FirebirdParser.System_actionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#component_actions.
    def enterComponent_actions(self, ctx:FirebirdParser.Component_actionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#component_actions.
    def exitComponent_actions(self, ctx:FirebirdParser.Component_actionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#component_action.
    def enterComponent_action(self, ctx:FirebirdParser.Component_actionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#component_action.
    def exitComponent_action(self, ctx:FirebirdParser.Component_actionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#role_audit_clause.
    def enterRole_audit_clause(self, ctx:FirebirdParser.Role_audit_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#role_audit_clause.
    def exitRole_audit_clause(self, ctx:FirebirdParser.Role_audit_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_controlfile.
    def enterCreate_controlfile(self, ctx:FirebirdParser.Create_controlfileContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_controlfile.
    def exitCreate_controlfile(self, ctx:FirebirdParser.Create_controlfileContext):
        pass


    # Enter a parse tree produced by FirebirdParser#controlfile_options.
    def enterControlfile_options(self, ctx:FirebirdParser.Controlfile_optionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#controlfile_options.
    def exitControlfile_options(self, ctx:FirebirdParser.Controlfile_optionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#logfile_clause.
    def enterLogfile_clause(self, ctx:FirebirdParser.Logfile_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#logfile_clause.
    def exitLogfile_clause(self, ctx:FirebirdParser.Logfile_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#character_set_clause.
    def enterCharacter_set_clause(self, ctx:FirebirdParser.Character_set_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#character_set_clause.
    def exitCharacter_set_clause(self, ctx:FirebirdParser.Character_set_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#file_specification.
    def enterFile_specification(self, ctx:FirebirdParser.File_specificationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#file_specification.
    def exitFile_specification(self, ctx:FirebirdParser.File_specificationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_diskgroup.
    def enterCreate_diskgroup(self, ctx:FirebirdParser.Create_diskgroupContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_diskgroup.
    def exitCreate_diskgroup(self, ctx:FirebirdParser.Create_diskgroupContext):
        pass


    # Enter a parse tree produced by FirebirdParser#qualified_disk_clause.
    def enterQualified_disk_clause(self, ctx:FirebirdParser.Qualified_disk_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#qualified_disk_clause.
    def exitQualified_disk_clause(self, ctx:FirebirdParser.Qualified_disk_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_edition.
    def enterCreate_edition(self, ctx:FirebirdParser.Create_editionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_edition.
    def exitCreate_edition(self, ctx:FirebirdParser.Create_editionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_flashback_archive.
    def enterCreate_flashback_archive(self, ctx:FirebirdParser.Create_flashback_archiveContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_flashback_archive.
    def exitCreate_flashback_archive(self, ctx:FirebirdParser.Create_flashback_archiveContext):
        pass


    # Enter a parse tree produced by FirebirdParser#flashback_archive_quota.
    def enterFlashback_archive_quota(self, ctx:FirebirdParser.Flashback_archive_quotaContext):
        pass

    # Exit a parse tree produced by FirebirdParser#flashback_archive_quota.
    def exitFlashback_archive_quota(self, ctx:FirebirdParser.Flashback_archive_quotaContext):
        pass


    # Enter a parse tree produced by FirebirdParser#flashback_archive_retention.
    def enterFlashback_archive_retention(self, ctx:FirebirdParser.Flashback_archive_retentionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#flashback_archive_retention.
    def exitFlashback_archive_retention(self, ctx:FirebirdParser.Flashback_archive_retentionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_hierarchy.
    def enterCreate_hierarchy(self, ctx:FirebirdParser.Create_hierarchyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_hierarchy.
    def exitCreate_hierarchy(self, ctx:FirebirdParser.Create_hierarchyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#hier_using_clause.
    def enterHier_using_clause(self, ctx:FirebirdParser.Hier_using_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#hier_using_clause.
    def exitHier_using_clause(self, ctx:FirebirdParser.Hier_using_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#level_hier_clause.
    def enterLevel_hier_clause(self, ctx:FirebirdParser.Level_hier_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#level_hier_clause.
    def exitLevel_hier_clause(self, ctx:FirebirdParser.Level_hier_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#hier_attrs_clause.
    def enterHier_attrs_clause(self, ctx:FirebirdParser.Hier_attrs_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#hier_attrs_clause.
    def exitHier_attrs_clause(self, ctx:FirebirdParser.Hier_attrs_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#hier_attr_clause.
    def enterHier_attr_clause(self, ctx:FirebirdParser.Hier_attr_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#hier_attr_clause.
    def exitHier_attr_clause(self, ctx:FirebirdParser.Hier_attr_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#hier_attr_name.
    def enterHier_attr_name(self, ctx:FirebirdParser.Hier_attr_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#hier_attr_name.
    def exitHier_attr_name(self, ctx:FirebirdParser.Hier_attr_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_index.
    def enterCreate_index(self, ctx:FirebirdParser.Create_indexContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_index.
    def exitCreate_index(self, ctx:FirebirdParser.Create_indexContext):
        pass


    # Enter a parse tree produced by FirebirdParser#cluster_index_clause.
    def enterCluster_index_clause(self, ctx:FirebirdParser.Cluster_index_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#cluster_index_clause.
    def exitCluster_index_clause(self, ctx:FirebirdParser.Cluster_index_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#cluster_name.
    def enterCluster_name(self, ctx:FirebirdParser.Cluster_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#cluster_name.
    def exitCluster_name(self, ctx:FirebirdParser.Cluster_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#table_index_clause.
    def enterTable_index_clause(self, ctx:FirebirdParser.Table_index_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#table_index_clause.
    def exitTable_index_clause(self, ctx:FirebirdParser.Table_index_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#bitmap_join_index_clause.
    def enterBitmap_join_index_clause(self, ctx:FirebirdParser.Bitmap_join_index_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#bitmap_join_index_clause.
    def exitBitmap_join_index_clause(self, ctx:FirebirdParser.Bitmap_join_index_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#index_expr.
    def enterIndex_expr(self, ctx:FirebirdParser.Index_exprContext):
        pass

    # Exit a parse tree produced by FirebirdParser#index_expr.
    def exitIndex_expr(self, ctx:FirebirdParser.Index_exprContext):
        pass


    # Enter a parse tree produced by FirebirdParser#index_properties.
    def enterIndex_properties(self, ctx:FirebirdParser.Index_propertiesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#index_properties.
    def exitIndex_properties(self, ctx:FirebirdParser.Index_propertiesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#domain_index_clause.
    def enterDomain_index_clause(self, ctx:FirebirdParser.Domain_index_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#domain_index_clause.
    def exitDomain_index_clause(self, ctx:FirebirdParser.Domain_index_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#local_domain_index_clause.
    def enterLocal_domain_index_clause(self, ctx:FirebirdParser.Local_domain_index_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#local_domain_index_clause.
    def exitLocal_domain_index_clause(self, ctx:FirebirdParser.Local_domain_index_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xmlindex_clause.
    def enterXmlindex_clause(self, ctx:FirebirdParser.Xmlindex_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xmlindex_clause.
    def exitXmlindex_clause(self, ctx:FirebirdParser.Xmlindex_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#local_xmlindex_clause.
    def enterLocal_xmlindex_clause(self, ctx:FirebirdParser.Local_xmlindex_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#local_xmlindex_clause.
    def exitLocal_xmlindex_clause(self, ctx:FirebirdParser.Local_xmlindex_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#global_partitioned_index.
    def enterGlobal_partitioned_index(self, ctx:FirebirdParser.Global_partitioned_indexContext):
        pass

    # Exit a parse tree produced by FirebirdParser#global_partitioned_index.
    def exitGlobal_partitioned_index(self, ctx:FirebirdParser.Global_partitioned_indexContext):
        pass


    # Enter a parse tree produced by FirebirdParser#index_partitioning_clause.
    def enterIndex_partitioning_clause(self, ctx:FirebirdParser.Index_partitioning_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#index_partitioning_clause.
    def exitIndex_partitioning_clause(self, ctx:FirebirdParser.Index_partitioning_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#index_partitioning_values_list.
    def enterIndex_partitioning_values_list(self, ctx:FirebirdParser.Index_partitioning_values_listContext):
        pass

    # Exit a parse tree produced by FirebirdParser#index_partitioning_values_list.
    def exitIndex_partitioning_values_list(self, ctx:FirebirdParser.Index_partitioning_values_listContext):
        pass


    # Enter a parse tree produced by FirebirdParser#local_partitioned_index.
    def enterLocal_partitioned_index(self, ctx:FirebirdParser.Local_partitioned_indexContext):
        pass

    # Exit a parse tree produced by FirebirdParser#local_partitioned_index.
    def exitLocal_partitioned_index(self, ctx:FirebirdParser.Local_partitioned_indexContext):
        pass


    # Enter a parse tree produced by FirebirdParser#on_range_partitioned_table.
    def enterOn_range_partitioned_table(self, ctx:FirebirdParser.On_range_partitioned_tableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#on_range_partitioned_table.
    def exitOn_range_partitioned_table(self, ctx:FirebirdParser.On_range_partitioned_tableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#on_list_partitioned_table.
    def enterOn_list_partitioned_table(self, ctx:FirebirdParser.On_list_partitioned_tableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#on_list_partitioned_table.
    def exitOn_list_partitioned_table(self, ctx:FirebirdParser.On_list_partitioned_tableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#partitioned_table.
    def enterPartitioned_table(self, ctx:FirebirdParser.Partitioned_tableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#partitioned_table.
    def exitPartitioned_table(self, ctx:FirebirdParser.Partitioned_tableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#on_hash_partitioned_table.
    def enterOn_hash_partitioned_table(self, ctx:FirebirdParser.On_hash_partitioned_tableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#on_hash_partitioned_table.
    def exitOn_hash_partitioned_table(self, ctx:FirebirdParser.On_hash_partitioned_tableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#on_hash_partitioned_clause.
    def enterOn_hash_partitioned_clause(self, ctx:FirebirdParser.On_hash_partitioned_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#on_hash_partitioned_clause.
    def exitOn_hash_partitioned_clause(self, ctx:FirebirdParser.On_hash_partitioned_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#on_comp_partitioned_table.
    def enterOn_comp_partitioned_table(self, ctx:FirebirdParser.On_comp_partitioned_tableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#on_comp_partitioned_table.
    def exitOn_comp_partitioned_table(self, ctx:FirebirdParser.On_comp_partitioned_tableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#on_comp_partitioned_clause.
    def enterOn_comp_partitioned_clause(self, ctx:FirebirdParser.On_comp_partitioned_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#on_comp_partitioned_clause.
    def exitOn_comp_partitioned_clause(self, ctx:FirebirdParser.On_comp_partitioned_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#index_subpartition_clause.
    def enterIndex_subpartition_clause(self, ctx:FirebirdParser.Index_subpartition_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#index_subpartition_clause.
    def exitIndex_subpartition_clause(self, ctx:FirebirdParser.Index_subpartition_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#index_subpartition_subclause.
    def enterIndex_subpartition_subclause(self, ctx:FirebirdParser.Index_subpartition_subclauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#index_subpartition_subclause.
    def exitIndex_subpartition_subclause(self, ctx:FirebirdParser.Index_subpartition_subclauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#odci_parameters.
    def enterOdci_parameters(self, ctx:FirebirdParser.Odci_parametersContext):
        pass

    # Exit a parse tree produced by FirebirdParser#odci_parameters.
    def exitOdci_parameters(self, ctx:FirebirdParser.Odci_parametersContext):
        pass


    # Enter a parse tree produced by FirebirdParser#indextype.
    def enterIndextype(self, ctx:FirebirdParser.IndextypeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#indextype.
    def exitIndextype(self, ctx:FirebirdParser.IndextypeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_index.
    def enterAlter_index(self, ctx:FirebirdParser.Alter_indexContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_index.
    def exitAlter_index(self, ctx:FirebirdParser.Alter_indexContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_index_ops_set1.
    def enterAlter_index_ops_set1(self, ctx:FirebirdParser.Alter_index_ops_set1Context):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_index_ops_set1.
    def exitAlter_index_ops_set1(self, ctx:FirebirdParser.Alter_index_ops_set1Context):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_index_ops_set2.
    def enterAlter_index_ops_set2(self, ctx:FirebirdParser.Alter_index_ops_set2Context):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_index_ops_set2.
    def exitAlter_index_ops_set2(self, ctx:FirebirdParser.Alter_index_ops_set2Context):
        pass


    # Enter a parse tree produced by FirebirdParser#visible_or_invisible.
    def enterVisible_or_invisible(self, ctx:FirebirdParser.Visible_or_invisibleContext):
        pass

    # Exit a parse tree produced by FirebirdParser#visible_or_invisible.
    def exitVisible_or_invisible(self, ctx:FirebirdParser.Visible_or_invisibleContext):
        pass


    # Enter a parse tree produced by FirebirdParser#monitoring_nomonitoring.
    def enterMonitoring_nomonitoring(self, ctx:FirebirdParser.Monitoring_nomonitoringContext):
        pass

    # Exit a parse tree produced by FirebirdParser#monitoring_nomonitoring.
    def exitMonitoring_nomonitoring(self, ctx:FirebirdParser.Monitoring_nomonitoringContext):
        pass


    # Enter a parse tree produced by FirebirdParser#rebuild_clause.
    def enterRebuild_clause(self, ctx:FirebirdParser.Rebuild_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#rebuild_clause.
    def exitRebuild_clause(self, ctx:FirebirdParser.Rebuild_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_index_partitioning.
    def enterAlter_index_partitioning(self, ctx:FirebirdParser.Alter_index_partitioningContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_index_partitioning.
    def exitAlter_index_partitioning(self, ctx:FirebirdParser.Alter_index_partitioningContext):
        pass


    # Enter a parse tree produced by FirebirdParser#modify_index_default_attrs.
    def enterModify_index_default_attrs(self, ctx:FirebirdParser.Modify_index_default_attrsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#modify_index_default_attrs.
    def exitModify_index_default_attrs(self, ctx:FirebirdParser.Modify_index_default_attrsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#add_hash_index_partition.
    def enterAdd_hash_index_partition(self, ctx:FirebirdParser.Add_hash_index_partitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#add_hash_index_partition.
    def exitAdd_hash_index_partition(self, ctx:FirebirdParser.Add_hash_index_partitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#coalesce_index_partition.
    def enterCoalesce_index_partition(self, ctx:FirebirdParser.Coalesce_index_partitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#coalesce_index_partition.
    def exitCoalesce_index_partition(self, ctx:FirebirdParser.Coalesce_index_partitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#modify_index_partition.
    def enterModify_index_partition(self, ctx:FirebirdParser.Modify_index_partitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#modify_index_partition.
    def exitModify_index_partition(self, ctx:FirebirdParser.Modify_index_partitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#modify_index_partitions_ops.
    def enterModify_index_partitions_ops(self, ctx:FirebirdParser.Modify_index_partitions_opsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#modify_index_partitions_ops.
    def exitModify_index_partitions_ops(self, ctx:FirebirdParser.Modify_index_partitions_opsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#rename_index_partition.
    def enterRename_index_partition(self, ctx:FirebirdParser.Rename_index_partitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#rename_index_partition.
    def exitRename_index_partition(self, ctx:FirebirdParser.Rename_index_partitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_index_partition.
    def enterDrop_index_partition(self, ctx:FirebirdParser.Drop_index_partitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_index_partition.
    def exitDrop_index_partition(self, ctx:FirebirdParser.Drop_index_partitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#split_index_partition.
    def enterSplit_index_partition(self, ctx:FirebirdParser.Split_index_partitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#split_index_partition.
    def exitSplit_index_partition(self, ctx:FirebirdParser.Split_index_partitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#index_partition_description.
    def enterIndex_partition_description(self, ctx:FirebirdParser.Index_partition_descriptionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#index_partition_description.
    def exitIndex_partition_description(self, ctx:FirebirdParser.Index_partition_descriptionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#modify_index_subpartition.
    def enterModify_index_subpartition(self, ctx:FirebirdParser.Modify_index_subpartitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#modify_index_subpartition.
    def exitModify_index_subpartition(self, ctx:FirebirdParser.Modify_index_subpartitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#partition_name_old.
    def enterPartition_name_old(self, ctx:FirebirdParser.Partition_name_oldContext):
        pass

    # Exit a parse tree produced by FirebirdParser#partition_name_old.
    def exitPartition_name_old(self, ctx:FirebirdParser.Partition_name_oldContext):
        pass


    # Enter a parse tree produced by FirebirdParser#new_partition_name.
    def enterNew_partition_name(self, ctx:FirebirdParser.New_partition_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#new_partition_name.
    def exitNew_partition_name(self, ctx:FirebirdParser.New_partition_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#new_index_name.
    def enterNew_index_name(self, ctx:FirebirdParser.New_index_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#new_index_name.
    def exitNew_index_name(self, ctx:FirebirdParser.New_index_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_inmemory_join_group.
    def enterAlter_inmemory_join_group(self, ctx:FirebirdParser.Alter_inmemory_join_groupContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_inmemory_join_group.
    def exitAlter_inmemory_join_group(self, ctx:FirebirdParser.Alter_inmemory_join_groupContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_user.
    def enterCreate_user(self, ctx:FirebirdParser.Create_userContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_user.
    def exitCreate_user(self, ctx:FirebirdParser.Create_userContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_user.
    def enterAlter_user(self, ctx:FirebirdParser.Alter_userContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_user.
    def exitAlter_user(self, ctx:FirebirdParser.Alter_userContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_user.
    def enterDrop_user(self, ctx:FirebirdParser.Drop_userContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_user.
    def exitDrop_user(self, ctx:FirebirdParser.Drop_userContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_identified_by.
    def enterAlter_identified_by(self, ctx:FirebirdParser.Alter_identified_byContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_identified_by.
    def exitAlter_identified_by(self, ctx:FirebirdParser.Alter_identified_byContext):
        pass


    # Enter a parse tree produced by FirebirdParser#identified_by.
    def enterIdentified_by(self, ctx:FirebirdParser.Identified_byContext):
        pass

    # Exit a parse tree produced by FirebirdParser#identified_by.
    def exitIdentified_by(self, ctx:FirebirdParser.Identified_byContext):
        pass


    # Enter a parse tree produced by FirebirdParser#identified_other_clause.
    def enterIdentified_other_clause(self, ctx:FirebirdParser.Identified_other_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#identified_other_clause.
    def exitIdentified_other_clause(self, ctx:FirebirdParser.Identified_other_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#user_tablespace_clause.
    def enterUser_tablespace_clause(self, ctx:FirebirdParser.User_tablespace_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#user_tablespace_clause.
    def exitUser_tablespace_clause(self, ctx:FirebirdParser.User_tablespace_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#quota_clause.
    def enterQuota_clause(self, ctx:FirebirdParser.Quota_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#quota_clause.
    def exitQuota_clause(self, ctx:FirebirdParser.Quota_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#profile_clause.
    def enterProfile_clause(self, ctx:FirebirdParser.Profile_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#profile_clause.
    def exitProfile_clause(self, ctx:FirebirdParser.Profile_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#role_clause.
    def enterRole_clause(self, ctx:FirebirdParser.Role_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#role_clause.
    def exitRole_clause(self, ctx:FirebirdParser.Role_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#user_default_role_clause.
    def enterUser_default_role_clause(self, ctx:FirebirdParser.User_default_role_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#user_default_role_clause.
    def exitUser_default_role_clause(self, ctx:FirebirdParser.User_default_role_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#password_expire_clause.
    def enterPassword_expire_clause(self, ctx:FirebirdParser.Password_expire_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#password_expire_clause.
    def exitPassword_expire_clause(self, ctx:FirebirdParser.Password_expire_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#user_lock_clause.
    def enterUser_lock_clause(self, ctx:FirebirdParser.User_lock_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#user_lock_clause.
    def exitUser_lock_clause(self, ctx:FirebirdParser.User_lock_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#user_editions_clause.
    def enterUser_editions_clause(self, ctx:FirebirdParser.User_editions_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#user_editions_clause.
    def exitUser_editions_clause(self, ctx:FirebirdParser.User_editions_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_user_editions_clause.
    def enterAlter_user_editions_clause(self, ctx:FirebirdParser.Alter_user_editions_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_user_editions_clause.
    def exitAlter_user_editions_clause(self, ctx:FirebirdParser.Alter_user_editions_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#proxy_clause.
    def enterProxy_clause(self, ctx:FirebirdParser.Proxy_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#proxy_clause.
    def exitProxy_clause(self, ctx:FirebirdParser.Proxy_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#container_names.
    def enterContainer_names(self, ctx:FirebirdParser.Container_namesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#container_names.
    def exitContainer_names(self, ctx:FirebirdParser.Container_namesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#set_container_data.
    def enterSet_container_data(self, ctx:FirebirdParser.Set_container_dataContext):
        pass

    # Exit a parse tree produced by FirebirdParser#set_container_data.
    def exitSet_container_data(self, ctx:FirebirdParser.Set_container_dataContext):
        pass


    # Enter a parse tree produced by FirebirdParser#add_rem_container_data.
    def enterAdd_rem_container_data(self, ctx:FirebirdParser.Add_rem_container_dataContext):
        pass

    # Exit a parse tree produced by FirebirdParser#add_rem_container_data.
    def exitAdd_rem_container_data(self, ctx:FirebirdParser.Add_rem_container_dataContext):
        pass


    # Enter a parse tree produced by FirebirdParser#container_data_clause.
    def enterContainer_data_clause(self, ctx:FirebirdParser.Container_data_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#container_data_clause.
    def exitContainer_data_clause(self, ctx:FirebirdParser.Container_data_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#administer_key_management.
    def enterAdminister_key_management(self, ctx:FirebirdParser.Administer_key_managementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#administer_key_management.
    def exitAdminister_key_management(self, ctx:FirebirdParser.Administer_key_managementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#keystore_management_clauses.
    def enterKeystore_management_clauses(self, ctx:FirebirdParser.Keystore_management_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#keystore_management_clauses.
    def exitKeystore_management_clauses(self, ctx:FirebirdParser.Keystore_management_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_keystore.
    def enterCreate_keystore(self, ctx:FirebirdParser.Create_keystoreContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_keystore.
    def exitCreate_keystore(self, ctx:FirebirdParser.Create_keystoreContext):
        pass


    # Enter a parse tree produced by FirebirdParser#open_keystore.
    def enterOpen_keystore(self, ctx:FirebirdParser.Open_keystoreContext):
        pass

    # Exit a parse tree produced by FirebirdParser#open_keystore.
    def exitOpen_keystore(self, ctx:FirebirdParser.Open_keystoreContext):
        pass


    # Enter a parse tree produced by FirebirdParser#force_keystore.
    def enterForce_keystore(self, ctx:FirebirdParser.Force_keystoreContext):
        pass

    # Exit a parse tree produced by FirebirdParser#force_keystore.
    def exitForce_keystore(self, ctx:FirebirdParser.Force_keystoreContext):
        pass


    # Enter a parse tree produced by FirebirdParser#close_keystore.
    def enterClose_keystore(self, ctx:FirebirdParser.Close_keystoreContext):
        pass

    # Exit a parse tree produced by FirebirdParser#close_keystore.
    def exitClose_keystore(self, ctx:FirebirdParser.Close_keystoreContext):
        pass


    # Enter a parse tree produced by FirebirdParser#backup_keystore.
    def enterBackup_keystore(self, ctx:FirebirdParser.Backup_keystoreContext):
        pass

    # Exit a parse tree produced by FirebirdParser#backup_keystore.
    def exitBackup_keystore(self, ctx:FirebirdParser.Backup_keystoreContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_keystore_password.
    def enterAlter_keystore_password(self, ctx:FirebirdParser.Alter_keystore_passwordContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_keystore_password.
    def exitAlter_keystore_password(self, ctx:FirebirdParser.Alter_keystore_passwordContext):
        pass


    # Enter a parse tree produced by FirebirdParser#merge_into_new_keystore.
    def enterMerge_into_new_keystore(self, ctx:FirebirdParser.Merge_into_new_keystoreContext):
        pass

    # Exit a parse tree produced by FirebirdParser#merge_into_new_keystore.
    def exitMerge_into_new_keystore(self, ctx:FirebirdParser.Merge_into_new_keystoreContext):
        pass


    # Enter a parse tree produced by FirebirdParser#merge_into_existing_keystore.
    def enterMerge_into_existing_keystore(self, ctx:FirebirdParser.Merge_into_existing_keystoreContext):
        pass

    # Exit a parse tree produced by FirebirdParser#merge_into_existing_keystore.
    def exitMerge_into_existing_keystore(self, ctx:FirebirdParser.Merge_into_existing_keystoreContext):
        pass


    # Enter a parse tree produced by FirebirdParser#isolate_keystore.
    def enterIsolate_keystore(self, ctx:FirebirdParser.Isolate_keystoreContext):
        pass

    # Exit a parse tree produced by FirebirdParser#isolate_keystore.
    def exitIsolate_keystore(self, ctx:FirebirdParser.Isolate_keystoreContext):
        pass


    # Enter a parse tree produced by FirebirdParser#unite_keystore.
    def enterUnite_keystore(self, ctx:FirebirdParser.Unite_keystoreContext):
        pass

    # Exit a parse tree produced by FirebirdParser#unite_keystore.
    def exitUnite_keystore(self, ctx:FirebirdParser.Unite_keystoreContext):
        pass


    # Enter a parse tree produced by FirebirdParser#key_management_clauses.
    def enterKey_management_clauses(self, ctx:FirebirdParser.Key_management_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#key_management_clauses.
    def exitKey_management_clauses(self, ctx:FirebirdParser.Key_management_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#set_key.
    def enterSet_key(self, ctx:FirebirdParser.Set_keyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#set_key.
    def exitSet_key(self, ctx:FirebirdParser.Set_keyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_key.
    def enterCreate_key(self, ctx:FirebirdParser.Create_keyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_key.
    def exitCreate_key(self, ctx:FirebirdParser.Create_keyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#mkid.
    def enterMkid(self, ctx:FirebirdParser.MkidContext):
        pass

    # Exit a parse tree produced by FirebirdParser#mkid.
    def exitMkid(self, ctx:FirebirdParser.MkidContext):
        pass


    # Enter a parse tree produced by FirebirdParser#mk.
    def enterMk(self, ctx:FirebirdParser.MkContext):
        pass

    # Exit a parse tree produced by FirebirdParser#mk.
    def exitMk(self, ctx:FirebirdParser.MkContext):
        pass


    # Enter a parse tree produced by FirebirdParser#use_key.
    def enterUse_key(self, ctx:FirebirdParser.Use_keyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#use_key.
    def exitUse_key(self, ctx:FirebirdParser.Use_keyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#set_key_tag.
    def enterSet_key_tag(self, ctx:FirebirdParser.Set_key_tagContext):
        pass

    # Exit a parse tree produced by FirebirdParser#set_key_tag.
    def exitSet_key_tag(self, ctx:FirebirdParser.Set_key_tagContext):
        pass


    # Enter a parse tree produced by FirebirdParser#export_keys.
    def enterExport_keys(self, ctx:FirebirdParser.Export_keysContext):
        pass

    # Exit a parse tree produced by FirebirdParser#export_keys.
    def exitExport_keys(self, ctx:FirebirdParser.Export_keysContext):
        pass


    # Enter a parse tree produced by FirebirdParser#import_keys.
    def enterImport_keys(self, ctx:FirebirdParser.Import_keysContext):
        pass

    # Exit a parse tree produced by FirebirdParser#import_keys.
    def exitImport_keys(self, ctx:FirebirdParser.Import_keysContext):
        pass


    # Enter a parse tree produced by FirebirdParser#migrate_keys.
    def enterMigrate_keys(self, ctx:FirebirdParser.Migrate_keysContext):
        pass

    # Exit a parse tree produced by FirebirdParser#migrate_keys.
    def exitMigrate_keys(self, ctx:FirebirdParser.Migrate_keysContext):
        pass


    # Enter a parse tree produced by FirebirdParser#reverse_migrate_keys.
    def enterReverse_migrate_keys(self, ctx:FirebirdParser.Reverse_migrate_keysContext):
        pass

    # Exit a parse tree produced by FirebirdParser#reverse_migrate_keys.
    def exitReverse_migrate_keys(self, ctx:FirebirdParser.Reverse_migrate_keysContext):
        pass


    # Enter a parse tree produced by FirebirdParser#move_keys.
    def enterMove_keys(self, ctx:FirebirdParser.Move_keysContext):
        pass

    # Exit a parse tree produced by FirebirdParser#move_keys.
    def exitMove_keys(self, ctx:FirebirdParser.Move_keysContext):
        pass


    # Enter a parse tree produced by FirebirdParser#identified_by_store.
    def enterIdentified_by_store(self, ctx:FirebirdParser.Identified_by_storeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#identified_by_store.
    def exitIdentified_by_store(self, ctx:FirebirdParser.Identified_by_storeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#using_algorithm_clause.
    def enterUsing_algorithm_clause(self, ctx:FirebirdParser.Using_algorithm_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#using_algorithm_clause.
    def exitUsing_algorithm_clause(self, ctx:FirebirdParser.Using_algorithm_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#using_tag_clause.
    def enterUsing_tag_clause(self, ctx:FirebirdParser.Using_tag_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#using_tag_clause.
    def exitUsing_tag_clause(self, ctx:FirebirdParser.Using_tag_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#secret_management_clauses.
    def enterSecret_management_clauses(self, ctx:FirebirdParser.Secret_management_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#secret_management_clauses.
    def exitSecret_management_clauses(self, ctx:FirebirdParser.Secret_management_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#add_update_secret.
    def enterAdd_update_secret(self, ctx:FirebirdParser.Add_update_secretContext):
        pass

    # Exit a parse tree produced by FirebirdParser#add_update_secret.
    def exitAdd_update_secret(self, ctx:FirebirdParser.Add_update_secretContext):
        pass


    # Enter a parse tree produced by FirebirdParser#delete_secret.
    def enterDelete_secret(self, ctx:FirebirdParser.Delete_secretContext):
        pass

    # Exit a parse tree produced by FirebirdParser#delete_secret.
    def exitDelete_secret(self, ctx:FirebirdParser.Delete_secretContext):
        pass


    # Enter a parse tree produced by FirebirdParser#add_update_secret_seps.
    def enterAdd_update_secret_seps(self, ctx:FirebirdParser.Add_update_secret_sepsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#add_update_secret_seps.
    def exitAdd_update_secret_seps(self, ctx:FirebirdParser.Add_update_secret_sepsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#delete_secret_seps.
    def enterDelete_secret_seps(self, ctx:FirebirdParser.Delete_secret_sepsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#delete_secret_seps.
    def exitDelete_secret_seps(self, ctx:FirebirdParser.Delete_secret_sepsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#zero_downtime_software_patching_clauses.
    def enterZero_downtime_software_patching_clauses(self, ctx:FirebirdParser.Zero_downtime_software_patching_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#zero_downtime_software_patching_clauses.
    def exitZero_downtime_software_patching_clauses(self, ctx:FirebirdParser.Zero_downtime_software_patching_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#with_backup_clause.
    def enterWith_backup_clause(self, ctx:FirebirdParser.With_backup_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#with_backup_clause.
    def exitWith_backup_clause(self, ctx:FirebirdParser.With_backup_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#identified_by_password_clause.
    def enterIdentified_by_password_clause(self, ctx:FirebirdParser.Identified_by_password_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#identified_by_password_clause.
    def exitIdentified_by_password_clause(self, ctx:FirebirdParser.Identified_by_password_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#keystore_password.
    def enterKeystore_password(self, ctx:FirebirdParser.Keystore_passwordContext):
        pass

    # Exit a parse tree produced by FirebirdParser#keystore_password.
    def exitKeystore_password(self, ctx:FirebirdParser.Keystore_passwordContext):
        pass


    # Enter a parse tree produced by FirebirdParser#path.
    def enterPath(self, ctx:FirebirdParser.PathContext):
        pass

    # Exit a parse tree produced by FirebirdParser#path.
    def exitPath(self, ctx:FirebirdParser.PathContext):
        pass


    # Enter a parse tree produced by FirebirdParser#secret.
    def enterSecret(self, ctx:FirebirdParser.SecretContext):
        pass

    # Exit a parse tree produced by FirebirdParser#secret.
    def exitSecret(self, ctx:FirebirdParser.SecretContext):
        pass


    # Enter a parse tree produced by FirebirdParser#analyze.
    def enterAnalyze(self, ctx:FirebirdParser.AnalyzeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#analyze.
    def exitAnalyze(self, ctx:FirebirdParser.AnalyzeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#partition_extention_clause.
    def enterPartition_extention_clause(self, ctx:FirebirdParser.Partition_extention_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#partition_extention_clause.
    def exitPartition_extention_clause(self, ctx:FirebirdParser.Partition_extention_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#validation_clauses.
    def enterValidation_clauses(self, ctx:FirebirdParser.Validation_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#validation_clauses.
    def exitValidation_clauses(self, ctx:FirebirdParser.Validation_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#compute_clauses.
    def enterCompute_clauses(self, ctx:FirebirdParser.Compute_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#compute_clauses.
    def exitCompute_clauses(self, ctx:FirebirdParser.Compute_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#for_clause.
    def enterFor_clause(self, ctx:FirebirdParser.For_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#for_clause.
    def exitFor_clause(self, ctx:FirebirdParser.For_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#online_or_offline.
    def enterOnline_or_offline(self, ctx:FirebirdParser.Online_or_offlineContext):
        pass

    # Exit a parse tree produced by FirebirdParser#online_or_offline.
    def exitOnline_or_offline(self, ctx:FirebirdParser.Online_or_offlineContext):
        pass


    # Enter a parse tree produced by FirebirdParser#into_clause1.
    def enterInto_clause1(self, ctx:FirebirdParser.Into_clause1Context):
        pass

    # Exit a parse tree produced by FirebirdParser#into_clause1.
    def exitInto_clause1(self, ctx:FirebirdParser.Into_clause1Context):
        pass


    # Enter a parse tree produced by FirebirdParser#partition_key_value.
    def enterPartition_key_value(self, ctx:FirebirdParser.Partition_key_valueContext):
        pass

    # Exit a parse tree produced by FirebirdParser#partition_key_value.
    def exitPartition_key_value(self, ctx:FirebirdParser.Partition_key_valueContext):
        pass


    # Enter a parse tree produced by FirebirdParser#subpartition_key_value.
    def enterSubpartition_key_value(self, ctx:FirebirdParser.Subpartition_key_valueContext):
        pass

    # Exit a parse tree produced by FirebirdParser#subpartition_key_value.
    def exitSubpartition_key_value(self, ctx:FirebirdParser.Subpartition_key_valueContext):
        pass


    # Enter a parse tree produced by FirebirdParser#associate_statistics.
    def enterAssociate_statistics(self, ctx:FirebirdParser.Associate_statisticsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#associate_statistics.
    def exitAssociate_statistics(self, ctx:FirebirdParser.Associate_statisticsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#column_association.
    def enterColumn_association(self, ctx:FirebirdParser.Column_associationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#column_association.
    def exitColumn_association(self, ctx:FirebirdParser.Column_associationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#function_association.
    def enterFunction_association(self, ctx:FirebirdParser.Function_associationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#function_association.
    def exitFunction_association(self, ctx:FirebirdParser.Function_associationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#indextype_name.
    def enterIndextype_name(self, ctx:FirebirdParser.Indextype_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#indextype_name.
    def exitIndextype_name(self, ctx:FirebirdParser.Indextype_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#using_statistics_type.
    def enterUsing_statistics_type(self, ctx:FirebirdParser.Using_statistics_typeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#using_statistics_type.
    def exitUsing_statistics_type(self, ctx:FirebirdParser.Using_statistics_typeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#statistics_type_name.
    def enterStatistics_type_name(self, ctx:FirebirdParser.Statistics_type_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#statistics_type_name.
    def exitStatistics_type_name(self, ctx:FirebirdParser.Statistics_type_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#default_cost_clause.
    def enterDefault_cost_clause(self, ctx:FirebirdParser.Default_cost_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#default_cost_clause.
    def exitDefault_cost_clause(self, ctx:FirebirdParser.Default_cost_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#cpu_cost.
    def enterCpu_cost(self, ctx:FirebirdParser.Cpu_costContext):
        pass

    # Exit a parse tree produced by FirebirdParser#cpu_cost.
    def exitCpu_cost(self, ctx:FirebirdParser.Cpu_costContext):
        pass


    # Enter a parse tree produced by FirebirdParser#io_cost.
    def enterIo_cost(self, ctx:FirebirdParser.Io_costContext):
        pass

    # Exit a parse tree produced by FirebirdParser#io_cost.
    def exitIo_cost(self, ctx:FirebirdParser.Io_costContext):
        pass


    # Enter a parse tree produced by FirebirdParser#network_cost.
    def enterNetwork_cost(self, ctx:FirebirdParser.Network_costContext):
        pass

    # Exit a parse tree produced by FirebirdParser#network_cost.
    def exitNetwork_cost(self, ctx:FirebirdParser.Network_costContext):
        pass


    # Enter a parse tree produced by FirebirdParser#default_selectivity_clause.
    def enterDefault_selectivity_clause(self, ctx:FirebirdParser.Default_selectivity_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#default_selectivity_clause.
    def exitDefault_selectivity_clause(self, ctx:FirebirdParser.Default_selectivity_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#default_selectivity.
    def enterDefault_selectivity(self, ctx:FirebirdParser.Default_selectivityContext):
        pass

    # Exit a parse tree produced by FirebirdParser#default_selectivity.
    def exitDefault_selectivity(self, ctx:FirebirdParser.Default_selectivityContext):
        pass


    # Enter a parse tree produced by FirebirdParser#storage_table_clause.
    def enterStorage_table_clause(self, ctx:FirebirdParser.Storage_table_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#storage_table_clause.
    def exitStorage_table_clause(self, ctx:FirebirdParser.Storage_table_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#unified_auditing.
    def enterUnified_auditing(self, ctx:FirebirdParser.Unified_auditingContext):
        pass

    # Exit a parse tree produced by FirebirdParser#unified_auditing.
    def exitUnified_auditing(self, ctx:FirebirdParser.Unified_auditingContext):
        pass


    # Enter a parse tree produced by FirebirdParser#policy_name.
    def enterPolicy_name(self, ctx:FirebirdParser.Policy_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#policy_name.
    def exitPolicy_name(self, ctx:FirebirdParser.Policy_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#audit_traditional.
    def enterAudit_traditional(self, ctx:FirebirdParser.Audit_traditionalContext):
        pass

    # Exit a parse tree produced by FirebirdParser#audit_traditional.
    def exitAudit_traditional(self, ctx:FirebirdParser.Audit_traditionalContext):
        pass


    # Enter a parse tree produced by FirebirdParser#audit_direct_path.
    def enterAudit_direct_path(self, ctx:FirebirdParser.Audit_direct_pathContext):
        pass

    # Exit a parse tree produced by FirebirdParser#audit_direct_path.
    def exitAudit_direct_path(self, ctx:FirebirdParser.Audit_direct_pathContext):
        pass


    # Enter a parse tree produced by FirebirdParser#audit_container_clause.
    def enterAudit_container_clause(self, ctx:FirebirdParser.Audit_container_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#audit_container_clause.
    def exitAudit_container_clause(self, ctx:FirebirdParser.Audit_container_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#audit_operation_clause.
    def enterAudit_operation_clause(self, ctx:FirebirdParser.Audit_operation_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#audit_operation_clause.
    def exitAudit_operation_clause(self, ctx:FirebirdParser.Audit_operation_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#auditing_by_clause.
    def enterAuditing_by_clause(self, ctx:FirebirdParser.Auditing_by_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#auditing_by_clause.
    def exitAuditing_by_clause(self, ctx:FirebirdParser.Auditing_by_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#audit_user.
    def enterAudit_user(self, ctx:FirebirdParser.Audit_userContext):
        pass

    # Exit a parse tree produced by FirebirdParser#audit_user.
    def exitAudit_user(self, ctx:FirebirdParser.Audit_userContext):
        pass


    # Enter a parse tree produced by FirebirdParser#audit_schema_object_clause.
    def enterAudit_schema_object_clause(self, ctx:FirebirdParser.Audit_schema_object_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#audit_schema_object_clause.
    def exitAudit_schema_object_clause(self, ctx:FirebirdParser.Audit_schema_object_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#sql_operation.
    def enterSql_operation(self, ctx:FirebirdParser.Sql_operationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#sql_operation.
    def exitSql_operation(self, ctx:FirebirdParser.Sql_operationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#auditing_on_clause.
    def enterAuditing_on_clause(self, ctx:FirebirdParser.Auditing_on_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#auditing_on_clause.
    def exitAuditing_on_clause(self, ctx:FirebirdParser.Auditing_on_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#model_name.
    def enterModel_name(self, ctx:FirebirdParser.Model_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#model_name.
    def exitModel_name(self, ctx:FirebirdParser.Model_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#object_name.
    def enterObject_name(self, ctx:FirebirdParser.Object_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#object_name.
    def exitObject_name(self, ctx:FirebirdParser.Object_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#profile_name.
    def enterProfile_name(self, ctx:FirebirdParser.Profile_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#profile_name.
    def exitProfile_name(self, ctx:FirebirdParser.Profile_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#sql_statement_shortcut.
    def enterSql_statement_shortcut(self, ctx:FirebirdParser.Sql_statement_shortcutContext):
        pass

    # Exit a parse tree produced by FirebirdParser#sql_statement_shortcut.
    def exitSql_statement_shortcut(self, ctx:FirebirdParser.Sql_statement_shortcutContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_index.
    def enterDrop_index(self, ctx:FirebirdParser.Drop_indexContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_index.
    def exitDrop_index(self, ctx:FirebirdParser.Drop_indexContext):
        pass


    # Enter a parse tree produced by FirebirdParser#disassociate_statistics.
    def enterDisassociate_statistics(self, ctx:FirebirdParser.Disassociate_statisticsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#disassociate_statistics.
    def exitDisassociate_statistics(self, ctx:FirebirdParser.Disassociate_statisticsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_indextype.
    def enterDrop_indextype(self, ctx:FirebirdParser.Drop_indextypeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_indextype.
    def exitDrop_indextype(self, ctx:FirebirdParser.Drop_indextypeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_inmemory_join_group.
    def enterDrop_inmemory_join_group(self, ctx:FirebirdParser.Drop_inmemory_join_groupContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_inmemory_join_group.
    def exitDrop_inmemory_join_group(self, ctx:FirebirdParser.Drop_inmemory_join_groupContext):
        pass


    # Enter a parse tree produced by FirebirdParser#flashback_table.
    def enterFlashback_table(self, ctx:FirebirdParser.Flashback_tableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#flashback_table.
    def exitFlashback_table(self, ctx:FirebirdParser.Flashback_tableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#restore_point.
    def enterRestore_point(self, ctx:FirebirdParser.Restore_pointContext):
        pass

    # Exit a parse tree produced by FirebirdParser#restore_point.
    def exitRestore_point(self, ctx:FirebirdParser.Restore_pointContext):
        pass


    # Enter a parse tree produced by FirebirdParser#purge_statement.
    def enterPurge_statement(self, ctx:FirebirdParser.Purge_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#purge_statement.
    def exitPurge_statement(self, ctx:FirebirdParser.Purge_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#noaudit_statement.
    def enterNoaudit_statement(self, ctx:FirebirdParser.Noaudit_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#noaudit_statement.
    def exitNoaudit_statement(self, ctx:FirebirdParser.Noaudit_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#rename_object.
    def enterRename_object(self, ctx:FirebirdParser.Rename_objectContext):
        pass

    # Exit a parse tree produced by FirebirdParser#rename_object.
    def exitRename_object(self, ctx:FirebirdParser.Rename_objectContext):
        pass


    # Enter a parse tree produced by FirebirdParser#grant_statement.
    def enterGrant_statement(self, ctx:FirebirdParser.Grant_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#grant_statement.
    def exitGrant_statement(self, ctx:FirebirdParser.Grant_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#container_clause.
    def enterContainer_clause(self, ctx:FirebirdParser.Container_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#container_clause.
    def exitContainer_clause(self, ctx:FirebirdParser.Container_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#revoke_statement.
    def enterRevoke_statement(self, ctx:FirebirdParser.Revoke_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#revoke_statement.
    def exitRevoke_statement(self, ctx:FirebirdParser.Revoke_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#revoke_system_privilege.
    def enterRevoke_system_privilege(self, ctx:FirebirdParser.Revoke_system_privilegeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#revoke_system_privilege.
    def exitRevoke_system_privilege(self, ctx:FirebirdParser.Revoke_system_privilegeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#revokee_clause.
    def enterRevokee_clause(self, ctx:FirebirdParser.Revokee_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#revokee_clause.
    def exitRevokee_clause(self, ctx:FirebirdParser.Revokee_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#revoke_object_privileges.
    def enterRevoke_object_privileges(self, ctx:FirebirdParser.Revoke_object_privilegesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#revoke_object_privileges.
    def exitRevoke_object_privileges(self, ctx:FirebirdParser.Revoke_object_privilegesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#on_object_clause.
    def enterOn_object_clause(self, ctx:FirebirdParser.On_object_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#on_object_clause.
    def exitOn_object_clause(self, ctx:FirebirdParser.On_object_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#revoke_roles_from_programs.
    def enterRevoke_roles_from_programs(self, ctx:FirebirdParser.Revoke_roles_from_programsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#revoke_roles_from_programs.
    def exitRevoke_roles_from_programs(self, ctx:FirebirdParser.Revoke_roles_from_programsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#program_unit.
    def enterProgram_unit(self, ctx:FirebirdParser.Program_unitContext):
        pass

    # Exit a parse tree produced by FirebirdParser#program_unit.
    def exitProgram_unit(self, ctx:FirebirdParser.Program_unitContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_dimension.
    def enterCreate_dimension(self, ctx:FirebirdParser.Create_dimensionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_dimension.
    def exitCreate_dimension(self, ctx:FirebirdParser.Create_dimensionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_directory.
    def enterCreate_directory(self, ctx:FirebirdParser.Create_directoryContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_directory.
    def exitCreate_directory(self, ctx:FirebirdParser.Create_directoryContext):
        pass


    # Enter a parse tree produced by FirebirdParser#directory_name.
    def enterDirectory_name(self, ctx:FirebirdParser.Directory_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#directory_name.
    def exitDirectory_name(self, ctx:FirebirdParser.Directory_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#directory_path.
    def enterDirectory_path(self, ctx:FirebirdParser.Directory_pathContext):
        pass

    # Exit a parse tree produced by FirebirdParser#directory_path.
    def exitDirectory_path(self, ctx:FirebirdParser.Directory_pathContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_inmemory_join_group.
    def enterCreate_inmemory_join_group(self, ctx:FirebirdParser.Create_inmemory_join_groupContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_inmemory_join_group.
    def exitCreate_inmemory_join_group(self, ctx:FirebirdParser.Create_inmemory_join_groupContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_hierarchy.
    def enterDrop_hierarchy(self, ctx:FirebirdParser.Drop_hierarchyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_hierarchy.
    def exitDrop_hierarchy(self, ctx:FirebirdParser.Drop_hierarchyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_library.
    def enterAlter_library(self, ctx:FirebirdParser.Alter_libraryContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_library.
    def exitAlter_library(self, ctx:FirebirdParser.Alter_libraryContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_java.
    def enterDrop_java(self, ctx:FirebirdParser.Drop_javaContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_java.
    def exitDrop_java(self, ctx:FirebirdParser.Drop_javaContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_library.
    def enterDrop_library(self, ctx:FirebirdParser.Drop_libraryContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_library.
    def exitDrop_library(self, ctx:FirebirdParser.Drop_libraryContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_java.
    def enterCreate_java(self, ctx:FirebirdParser.Create_javaContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_java.
    def exitCreate_java(self, ctx:FirebirdParser.Create_javaContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_library.
    def enterCreate_library(self, ctx:FirebirdParser.Create_libraryContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_library.
    def exitCreate_library(self, ctx:FirebirdParser.Create_libraryContext):
        pass


    # Enter a parse tree produced by FirebirdParser#plsql_library_source.
    def enterPlsql_library_source(self, ctx:FirebirdParser.Plsql_library_sourceContext):
        pass

    # Exit a parse tree produced by FirebirdParser#plsql_library_source.
    def exitPlsql_library_source(self, ctx:FirebirdParser.Plsql_library_sourceContext):
        pass


    # Enter a parse tree produced by FirebirdParser#credential_name.
    def enterCredential_name(self, ctx:FirebirdParser.Credential_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#credential_name.
    def exitCredential_name(self, ctx:FirebirdParser.Credential_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#library_editionable.
    def enterLibrary_editionable(self, ctx:FirebirdParser.Library_editionableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#library_editionable.
    def exitLibrary_editionable(self, ctx:FirebirdParser.Library_editionableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#library_debug.
    def enterLibrary_debug(self, ctx:FirebirdParser.Library_debugContext):
        pass

    # Exit a parse tree produced by FirebirdParser#library_debug.
    def exitLibrary_debug(self, ctx:FirebirdParser.Library_debugContext):
        pass


    # Enter a parse tree produced by FirebirdParser#compiler_parameters_clause.
    def enterCompiler_parameters_clause(self, ctx:FirebirdParser.Compiler_parameters_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#compiler_parameters_clause.
    def exitCompiler_parameters_clause(self, ctx:FirebirdParser.Compiler_parameters_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#parameter_value.
    def enterParameter_value(self, ctx:FirebirdParser.Parameter_valueContext):
        pass

    # Exit a parse tree produced by FirebirdParser#parameter_value.
    def exitParameter_value(self, ctx:FirebirdParser.Parameter_valueContext):
        pass


    # Enter a parse tree produced by FirebirdParser#library_name.
    def enterLibrary_name(self, ctx:FirebirdParser.Library_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#library_name.
    def exitLibrary_name(self, ctx:FirebirdParser.Library_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_dimension.
    def enterAlter_dimension(self, ctx:FirebirdParser.Alter_dimensionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_dimension.
    def exitAlter_dimension(self, ctx:FirebirdParser.Alter_dimensionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#level_clause.
    def enterLevel_clause(self, ctx:FirebirdParser.Level_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#level_clause.
    def exitLevel_clause(self, ctx:FirebirdParser.Level_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#hierarchy_clause.
    def enterHierarchy_clause(self, ctx:FirebirdParser.Hierarchy_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#hierarchy_clause.
    def exitHierarchy_clause(self, ctx:FirebirdParser.Hierarchy_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#dimension_join_clause.
    def enterDimension_join_clause(self, ctx:FirebirdParser.Dimension_join_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#dimension_join_clause.
    def exitDimension_join_clause(self, ctx:FirebirdParser.Dimension_join_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#attribute_clause.
    def enterAttribute_clause(self, ctx:FirebirdParser.Attribute_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#attribute_clause.
    def exitAttribute_clause(self, ctx:FirebirdParser.Attribute_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#extended_attribute_clause.
    def enterExtended_attribute_clause(self, ctx:FirebirdParser.Extended_attribute_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#extended_attribute_clause.
    def exitExtended_attribute_clause(self, ctx:FirebirdParser.Extended_attribute_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#column_one_or_more_sub_clause.
    def enterColumn_one_or_more_sub_clause(self, ctx:FirebirdParser.Column_one_or_more_sub_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#column_one_or_more_sub_clause.
    def exitColumn_one_or_more_sub_clause(self, ctx:FirebirdParser.Column_one_or_more_sub_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_view.
    def enterAlter_view(self, ctx:FirebirdParser.Alter_viewContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_view.
    def exitAlter_view(self, ctx:FirebirdParser.Alter_viewContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_view_editionable.
    def enterAlter_view_editionable(self, ctx:FirebirdParser.Alter_view_editionableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_view_editionable.
    def exitAlter_view_editionable(self, ctx:FirebirdParser.Alter_view_editionableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_view.
    def enterCreate_view(self, ctx:FirebirdParser.Create_viewContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_view.
    def exitCreate_view(self, ctx:FirebirdParser.Create_viewContext):
        pass


    # Enter a parse tree produced by FirebirdParser#editioning_clause.
    def enterEditioning_clause(self, ctx:FirebirdParser.Editioning_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#editioning_clause.
    def exitEditioning_clause(self, ctx:FirebirdParser.Editioning_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#view_options.
    def enterView_options(self, ctx:FirebirdParser.View_optionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#view_options.
    def exitView_options(self, ctx:FirebirdParser.View_optionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#view_alias_constraint.
    def enterView_alias_constraint(self, ctx:FirebirdParser.View_alias_constraintContext):
        pass

    # Exit a parse tree produced by FirebirdParser#view_alias_constraint.
    def exitView_alias_constraint(self, ctx:FirebirdParser.View_alias_constraintContext):
        pass


    # Enter a parse tree produced by FirebirdParser#object_view_clause.
    def enterObject_view_clause(self, ctx:FirebirdParser.Object_view_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#object_view_clause.
    def exitObject_view_clause(self, ctx:FirebirdParser.Object_view_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#inline_constraint.
    def enterInline_constraint(self, ctx:FirebirdParser.Inline_constraintContext):
        pass

    # Exit a parse tree produced by FirebirdParser#inline_constraint.
    def exitInline_constraint(self, ctx:FirebirdParser.Inline_constraintContext):
        pass


    # Enter a parse tree produced by FirebirdParser#inline_ref_constraint.
    def enterInline_ref_constraint(self, ctx:FirebirdParser.Inline_ref_constraintContext):
        pass

    # Exit a parse tree produced by FirebirdParser#inline_ref_constraint.
    def exitInline_ref_constraint(self, ctx:FirebirdParser.Inline_ref_constraintContext):
        pass


    # Enter a parse tree produced by FirebirdParser#out_of_line_ref_constraint.
    def enterOut_of_line_ref_constraint(self, ctx:FirebirdParser.Out_of_line_ref_constraintContext):
        pass

    # Exit a parse tree produced by FirebirdParser#out_of_line_ref_constraint.
    def exitOut_of_line_ref_constraint(self, ctx:FirebirdParser.Out_of_line_ref_constraintContext):
        pass


    # Enter a parse tree produced by FirebirdParser#out_of_line_constraint.
    def enterOut_of_line_constraint(self, ctx:FirebirdParser.Out_of_line_constraintContext):
        pass

    # Exit a parse tree produced by FirebirdParser#out_of_line_constraint.
    def exitOut_of_line_constraint(self, ctx:FirebirdParser.Out_of_line_constraintContext):
        pass


    # Enter a parse tree produced by FirebirdParser#constraint_state.
    def enterConstraint_state(self, ctx:FirebirdParser.Constraint_stateContext):
        pass

    # Exit a parse tree produced by FirebirdParser#constraint_state.
    def exitConstraint_state(self, ctx:FirebirdParser.Constraint_stateContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xmltype_view_clause.
    def enterXmltype_view_clause(self, ctx:FirebirdParser.Xmltype_view_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xmltype_view_clause.
    def exitXmltype_view_clause(self, ctx:FirebirdParser.Xmltype_view_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xml_schema_spec.
    def enterXml_schema_spec(self, ctx:FirebirdParser.Xml_schema_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xml_schema_spec.
    def exitXml_schema_spec(self, ctx:FirebirdParser.Xml_schema_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xml_schema_url.
    def enterXml_schema_url(self, ctx:FirebirdParser.Xml_schema_urlContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xml_schema_url.
    def exitXml_schema_url(self, ctx:FirebirdParser.Xml_schema_urlContext):
        pass


    # Enter a parse tree produced by FirebirdParser#element.
    def enterElement(self, ctx:FirebirdParser.ElementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#element.
    def exitElement(self, ctx:FirebirdParser.ElementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_tablespace.
    def enterAlter_tablespace(self, ctx:FirebirdParser.Alter_tablespaceContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_tablespace.
    def exitAlter_tablespace(self, ctx:FirebirdParser.Alter_tablespaceContext):
        pass


    # Enter a parse tree produced by FirebirdParser#datafile_tempfile_clauses.
    def enterDatafile_tempfile_clauses(self, ctx:FirebirdParser.Datafile_tempfile_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#datafile_tempfile_clauses.
    def exitDatafile_tempfile_clauses(self, ctx:FirebirdParser.Datafile_tempfile_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#tablespace_logging_clauses.
    def enterTablespace_logging_clauses(self, ctx:FirebirdParser.Tablespace_logging_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#tablespace_logging_clauses.
    def exitTablespace_logging_clauses(self, ctx:FirebirdParser.Tablespace_logging_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#tablespace_group_clause.
    def enterTablespace_group_clause(self, ctx:FirebirdParser.Tablespace_group_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#tablespace_group_clause.
    def exitTablespace_group_clause(self, ctx:FirebirdParser.Tablespace_group_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#tablespace_group_name.
    def enterTablespace_group_name(self, ctx:FirebirdParser.Tablespace_group_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#tablespace_group_name.
    def exitTablespace_group_name(self, ctx:FirebirdParser.Tablespace_group_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#tablespace_state_clauses.
    def enterTablespace_state_clauses(self, ctx:FirebirdParser.Tablespace_state_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#tablespace_state_clauses.
    def exitTablespace_state_clauses(self, ctx:FirebirdParser.Tablespace_state_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#flashback_mode_clause.
    def enterFlashback_mode_clause(self, ctx:FirebirdParser.Flashback_mode_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#flashback_mode_clause.
    def exitFlashback_mode_clause(self, ctx:FirebirdParser.Flashback_mode_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#new_tablespace_name.
    def enterNew_tablespace_name(self, ctx:FirebirdParser.New_tablespace_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#new_tablespace_name.
    def exitNew_tablespace_name(self, ctx:FirebirdParser.New_tablespace_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_tablespace.
    def enterCreate_tablespace(self, ctx:FirebirdParser.Create_tablespaceContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_tablespace.
    def exitCreate_tablespace(self, ctx:FirebirdParser.Create_tablespaceContext):
        pass


    # Enter a parse tree produced by FirebirdParser#permanent_tablespace_clause.
    def enterPermanent_tablespace_clause(self, ctx:FirebirdParser.Permanent_tablespace_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#permanent_tablespace_clause.
    def exitPermanent_tablespace_clause(self, ctx:FirebirdParser.Permanent_tablespace_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#tablespace_encryption_spec.
    def enterTablespace_encryption_spec(self, ctx:FirebirdParser.Tablespace_encryption_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#tablespace_encryption_spec.
    def exitTablespace_encryption_spec(self, ctx:FirebirdParser.Tablespace_encryption_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#logging_clause.
    def enterLogging_clause(self, ctx:FirebirdParser.Logging_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#logging_clause.
    def exitLogging_clause(self, ctx:FirebirdParser.Logging_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#extent_management_clause.
    def enterExtent_management_clause(self, ctx:FirebirdParser.Extent_management_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#extent_management_clause.
    def exitExtent_management_clause(self, ctx:FirebirdParser.Extent_management_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#segment_management_clause.
    def enterSegment_management_clause(self, ctx:FirebirdParser.Segment_management_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#segment_management_clause.
    def exitSegment_management_clause(self, ctx:FirebirdParser.Segment_management_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#temporary_tablespace_clause.
    def enterTemporary_tablespace_clause(self, ctx:FirebirdParser.Temporary_tablespace_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#temporary_tablespace_clause.
    def exitTemporary_tablespace_clause(self, ctx:FirebirdParser.Temporary_tablespace_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#undo_tablespace_clause.
    def enterUndo_tablespace_clause(self, ctx:FirebirdParser.Undo_tablespace_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#undo_tablespace_clause.
    def exitUndo_tablespace_clause(self, ctx:FirebirdParser.Undo_tablespace_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#tablespace_retention_clause.
    def enterTablespace_retention_clause(self, ctx:FirebirdParser.Tablespace_retention_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#tablespace_retention_clause.
    def exitTablespace_retention_clause(self, ctx:FirebirdParser.Tablespace_retention_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_tablespace_set.
    def enterCreate_tablespace_set(self, ctx:FirebirdParser.Create_tablespace_setContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_tablespace_set.
    def exitCreate_tablespace_set(self, ctx:FirebirdParser.Create_tablespace_setContext):
        pass


    # Enter a parse tree produced by FirebirdParser#permanent_tablespace_attrs.
    def enterPermanent_tablespace_attrs(self, ctx:FirebirdParser.Permanent_tablespace_attrsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#permanent_tablespace_attrs.
    def exitPermanent_tablespace_attrs(self, ctx:FirebirdParser.Permanent_tablespace_attrsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#tablespace_encryption_clause.
    def enterTablespace_encryption_clause(self, ctx:FirebirdParser.Tablespace_encryption_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#tablespace_encryption_clause.
    def exitTablespace_encryption_clause(self, ctx:FirebirdParser.Tablespace_encryption_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#default_tablespace_params.
    def enterDefault_tablespace_params(self, ctx:FirebirdParser.Default_tablespace_paramsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#default_tablespace_params.
    def exitDefault_tablespace_params(self, ctx:FirebirdParser.Default_tablespace_paramsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#default_table_compression.
    def enterDefault_table_compression(self, ctx:FirebirdParser.Default_table_compressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#default_table_compression.
    def exitDefault_table_compression(self, ctx:FirebirdParser.Default_table_compressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#low_high.
    def enterLow_high(self, ctx:FirebirdParser.Low_highContext):
        pass

    # Exit a parse tree produced by FirebirdParser#low_high.
    def exitLow_high(self, ctx:FirebirdParser.Low_highContext):
        pass


    # Enter a parse tree produced by FirebirdParser#default_index_compression.
    def enterDefault_index_compression(self, ctx:FirebirdParser.Default_index_compressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#default_index_compression.
    def exitDefault_index_compression(self, ctx:FirebirdParser.Default_index_compressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#inmmemory_clause.
    def enterInmmemory_clause(self, ctx:FirebirdParser.Inmmemory_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#inmmemory_clause.
    def exitInmmemory_clause(self, ctx:FirebirdParser.Inmmemory_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#datafile_specification.
    def enterDatafile_specification(self, ctx:FirebirdParser.Datafile_specificationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#datafile_specification.
    def exitDatafile_specification(self, ctx:FirebirdParser.Datafile_specificationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#tempfile_specification.
    def enterTempfile_specification(self, ctx:FirebirdParser.Tempfile_specificationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#tempfile_specification.
    def exitTempfile_specification(self, ctx:FirebirdParser.Tempfile_specificationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#datafile_tempfile_spec.
    def enterDatafile_tempfile_spec(self, ctx:FirebirdParser.Datafile_tempfile_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#datafile_tempfile_spec.
    def exitDatafile_tempfile_spec(self, ctx:FirebirdParser.Datafile_tempfile_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#redo_log_file_spec.
    def enterRedo_log_file_spec(self, ctx:FirebirdParser.Redo_log_file_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#redo_log_file_spec.
    def exitRedo_log_file_spec(self, ctx:FirebirdParser.Redo_log_file_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#autoextend_clause.
    def enterAutoextend_clause(self, ctx:FirebirdParser.Autoextend_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#autoextend_clause.
    def exitAutoextend_clause(self, ctx:FirebirdParser.Autoextend_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#maxsize_clause.
    def enterMaxsize_clause(self, ctx:FirebirdParser.Maxsize_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#maxsize_clause.
    def exitMaxsize_clause(self, ctx:FirebirdParser.Maxsize_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#build_clause.
    def enterBuild_clause(self, ctx:FirebirdParser.Build_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#build_clause.
    def exitBuild_clause(self, ctx:FirebirdParser.Build_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#parallel_clause.
    def enterParallel_clause(self, ctx:FirebirdParser.Parallel_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#parallel_clause.
    def exitParallel_clause(self, ctx:FirebirdParser.Parallel_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#parallel_instances_clause.
    def enterParallel_instances_clause(self, ctx:FirebirdParser.Parallel_instances_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#parallel_instances_clause.
    def exitParallel_instances_clause(self, ctx:FirebirdParser.Parallel_instances_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_materialized_view.
    def enterAlter_materialized_view(self, ctx:FirebirdParser.Alter_materialized_viewContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_materialized_view.
    def exitAlter_materialized_view(self, ctx:FirebirdParser.Alter_materialized_viewContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_mv_option1.
    def enterAlter_mv_option1(self, ctx:FirebirdParser.Alter_mv_option1Context):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_mv_option1.
    def exitAlter_mv_option1(self, ctx:FirebirdParser.Alter_mv_option1Context):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_mv_refresh.
    def enterAlter_mv_refresh(self, ctx:FirebirdParser.Alter_mv_refreshContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_mv_refresh.
    def exitAlter_mv_refresh(self, ctx:FirebirdParser.Alter_mv_refreshContext):
        pass


    # Enter a parse tree produced by FirebirdParser#rollback_segment.
    def enterRollback_segment(self, ctx:FirebirdParser.Rollback_segmentContext):
        pass

    # Exit a parse tree produced by FirebirdParser#rollback_segment.
    def exitRollback_segment(self, ctx:FirebirdParser.Rollback_segmentContext):
        pass


    # Enter a parse tree produced by FirebirdParser#modify_mv_column_clause.
    def enterModify_mv_column_clause(self, ctx:FirebirdParser.Modify_mv_column_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#modify_mv_column_clause.
    def exitModify_mv_column_clause(self, ctx:FirebirdParser.Modify_mv_column_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_materialized_view_log.
    def enterAlter_materialized_view_log(self, ctx:FirebirdParser.Alter_materialized_view_logContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_materialized_view_log.
    def exitAlter_materialized_view_log(self, ctx:FirebirdParser.Alter_materialized_view_logContext):
        pass


    # Enter a parse tree produced by FirebirdParser#add_mv_log_column_clause.
    def enterAdd_mv_log_column_clause(self, ctx:FirebirdParser.Add_mv_log_column_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#add_mv_log_column_clause.
    def exitAdd_mv_log_column_clause(self, ctx:FirebirdParser.Add_mv_log_column_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#move_mv_log_clause.
    def enterMove_mv_log_clause(self, ctx:FirebirdParser.Move_mv_log_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#move_mv_log_clause.
    def exitMove_mv_log_clause(self, ctx:FirebirdParser.Move_mv_log_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#mv_log_augmentation.
    def enterMv_log_augmentation(self, ctx:FirebirdParser.Mv_log_augmentationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#mv_log_augmentation.
    def exitMv_log_augmentation(self, ctx:FirebirdParser.Mv_log_augmentationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_materialized_view_log.
    def enterCreate_materialized_view_log(self, ctx:FirebirdParser.Create_materialized_view_logContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_materialized_view_log.
    def exitCreate_materialized_view_log(self, ctx:FirebirdParser.Create_materialized_view_logContext):
        pass


    # Enter a parse tree produced by FirebirdParser#new_values_clause.
    def enterNew_values_clause(self, ctx:FirebirdParser.New_values_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#new_values_clause.
    def exitNew_values_clause(self, ctx:FirebirdParser.New_values_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#mv_log_purge_clause.
    def enterMv_log_purge_clause(self, ctx:FirebirdParser.Mv_log_purge_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#mv_log_purge_clause.
    def exitMv_log_purge_clause(self, ctx:FirebirdParser.Mv_log_purge_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_materialized_zonemap.
    def enterCreate_materialized_zonemap(self, ctx:FirebirdParser.Create_materialized_zonemapContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_materialized_zonemap.
    def exitCreate_materialized_zonemap(self, ctx:FirebirdParser.Create_materialized_zonemapContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_materialized_zonemap.
    def enterAlter_materialized_zonemap(self, ctx:FirebirdParser.Alter_materialized_zonemapContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_materialized_zonemap.
    def exitAlter_materialized_zonemap(self, ctx:FirebirdParser.Alter_materialized_zonemapContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_materialized_zonemap.
    def enterDrop_materialized_zonemap(self, ctx:FirebirdParser.Drop_materialized_zonemapContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_materialized_zonemap.
    def exitDrop_materialized_zonemap(self, ctx:FirebirdParser.Drop_materialized_zonemapContext):
        pass


    # Enter a parse tree produced by FirebirdParser#zonemap_refresh_clause.
    def enterZonemap_refresh_clause(self, ctx:FirebirdParser.Zonemap_refresh_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#zonemap_refresh_clause.
    def exitZonemap_refresh_clause(self, ctx:FirebirdParser.Zonemap_refresh_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#zonemap_attributes.
    def enterZonemap_attributes(self, ctx:FirebirdParser.Zonemap_attributesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#zonemap_attributes.
    def exitZonemap_attributes(self, ctx:FirebirdParser.Zonemap_attributesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#zonemap_name.
    def enterZonemap_name(self, ctx:FirebirdParser.Zonemap_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#zonemap_name.
    def exitZonemap_name(self, ctx:FirebirdParser.Zonemap_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#operator_name.
    def enterOperator_name(self, ctx:FirebirdParser.Operator_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#operator_name.
    def exitOperator_name(self, ctx:FirebirdParser.Operator_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#operator_function_name.
    def enterOperator_function_name(self, ctx:FirebirdParser.Operator_function_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#operator_function_name.
    def exitOperator_function_name(self, ctx:FirebirdParser.Operator_function_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_zonemap_on_table.
    def enterCreate_zonemap_on_table(self, ctx:FirebirdParser.Create_zonemap_on_tableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_zonemap_on_table.
    def exitCreate_zonemap_on_table(self, ctx:FirebirdParser.Create_zonemap_on_tableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_zonemap_as_subquery.
    def enterCreate_zonemap_as_subquery(self, ctx:FirebirdParser.Create_zonemap_as_subqueryContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_zonemap_as_subquery.
    def exitCreate_zonemap_as_subquery(self, ctx:FirebirdParser.Create_zonemap_as_subqueryContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_operator.
    def enterAlter_operator(self, ctx:FirebirdParser.Alter_operatorContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_operator.
    def exitAlter_operator(self, ctx:FirebirdParser.Alter_operatorContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_operator.
    def enterDrop_operator(self, ctx:FirebirdParser.Drop_operatorContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_operator.
    def exitDrop_operator(self, ctx:FirebirdParser.Drop_operatorContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_operator.
    def enterCreate_operator(self, ctx:FirebirdParser.Create_operatorContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_operator.
    def exitCreate_operator(self, ctx:FirebirdParser.Create_operatorContext):
        pass


    # Enter a parse tree produced by FirebirdParser#binding_clause.
    def enterBinding_clause(self, ctx:FirebirdParser.Binding_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#binding_clause.
    def exitBinding_clause(self, ctx:FirebirdParser.Binding_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#add_binding_clause.
    def enterAdd_binding_clause(self, ctx:FirebirdParser.Add_binding_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#add_binding_clause.
    def exitAdd_binding_clause(self, ctx:FirebirdParser.Add_binding_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#implementation_clause.
    def enterImplementation_clause(self, ctx:FirebirdParser.Implementation_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#implementation_clause.
    def exitImplementation_clause(self, ctx:FirebirdParser.Implementation_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#primary_operator_list.
    def enterPrimary_operator_list(self, ctx:FirebirdParser.Primary_operator_listContext):
        pass

    # Exit a parse tree produced by FirebirdParser#primary_operator_list.
    def exitPrimary_operator_list(self, ctx:FirebirdParser.Primary_operator_listContext):
        pass


    # Enter a parse tree produced by FirebirdParser#primary_operator_item.
    def enterPrimary_operator_item(self, ctx:FirebirdParser.Primary_operator_itemContext):
        pass

    # Exit a parse tree produced by FirebirdParser#primary_operator_item.
    def exitPrimary_operator_item(self, ctx:FirebirdParser.Primary_operator_itemContext):
        pass


    # Enter a parse tree produced by FirebirdParser#operator_context_clause.
    def enterOperator_context_clause(self, ctx:FirebirdParser.Operator_context_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#operator_context_clause.
    def exitOperator_context_clause(self, ctx:FirebirdParser.Operator_context_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#using_function_clause.
    def enterUsing_function_clause(self, ctx:FirebirdParser.Using_function_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#using_function_clause.
    def exitUsing_function_clause(self, ctx:FirebirdParser.Using_function_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_binding_clause.
    def enterDrop_binding_clause(self, ctx:FirebirdParser.Drop_binding_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_binding_clause.
    def exitDrop_binding_clause(self, ctx:FirebirdParser.Drop_binding_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_materialized_view.
    def enterCreate_materialized_view(self, ctx:FirebirdParser.Create_materialized_viewContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_materialized_view.
    def exitCreate_materialized_view(self, ctx:FirebirdParser.Create_materialized_viewContext):
        pass


    # Enter a parse tree produced by FirebirdParser#scoped_table_ref_constraint.
    def enterScoped_table_ref_constraint(self, ctx:FirebirdParser.Scoped_table_ref_constraintContext):
        pass

    # Exit a parse tree produced by FirebirdParser#scoped_table_ref_constraint.
    def exitScoped_table_ref_constraint(self, ctx:FirebirdParser.Scoped_table_ref_constraintContext):
        pass


    # Enter a parse tree produced by FirebirdParser#mv_column_alias.
    def enterMv_column_alias(self, ctx:FirebirdParser.Mv_column_aliasContext):
        pass

    # Exit a parse tree produced by FirebirdParser#mv_column_alias.
    def exitMv_column_alias(self, ctx:FirebirdParser.Mv_column_aliasContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_mv_refresh.
    def enterCreate_mv_refresh(self, ctx:FirebirdParser.Create_mv_refreshContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_mv_refresh.
    def exitCreate_mv_refresh(self, ctx:FirebirdParser.Create_mv_refreshContext):
        pass


    # Enter a parse tree produced by FirebirdParser#query_rewrite_clause.
    def enterQuery_rewrite_clause(self, ctx:FirebirdParser.Query_rewrite_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#query_rewrite_clause.
    def exitQuery_rewrite_clause(self, ctx:FirebirdParser.Query_rewrite_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#unusable_editions_clause.
    def enterUnusable_editions_clause(self, ctx:FirebirdParser.Unusable_editions_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#unusable_editions_clause.
    def exitUnusable_editions_clause(self, ctx:FirebirdParser.Unusable_editions_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_materialized_view.
    def enterDrop_materialized_view(self, ctx:FirebirdParser.Drop_materialized_viewContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_materialized_view.
    def exitDrop_materialized_view(self, ctx:FirebirdParser.Drop_materialized_viewContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_materialized_view_log.
    def enterDrop_materialized_view_log(self, ctx:FirebirdParser.Drop_materialized_view_logContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_materialized_view_log.
    def exitDrop_materialized_view_log(self, ctx:FirebirdParser.Drop_materialized_view_logContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_context.
    def enterCreate_context(self, ctx:FirebirdParser.Create_contextContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_context.
    def exitCreate_context(self, ctx:FirebirdParser.Create_contextContext):
        pass


    # Enter a parse tree produced by FirebirdParser#firebird_namespace.
    def enterFirebird_namespace(self, ctx:FirebirdParser.Firebird_namespaceContext):
        pass

    # Exit a parse tree produced by FirebirdParser#firebird_namespace.
    def exitFirebird_namespace(self, ctx:FirebirdParser.Firebird_namespaceContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_cluster.
    def enterCreate_cluster(self, ctx:FirebirdParser.Create_clusterContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_cluster.
    def exitCreate_cluster(self, ctx:FirebirdParser.Create_clusterContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_profile.
    def enterCreate_profile(self, ctx:FirebirdParser.Create_profileContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_profile.
    def exitCreate_profile(self, ctx:FirebirdParser.Create_profileContext):
        pass


    # Enter a parse tree produced by FirebirdParser#resource_parameters.
    def enterResource_parameters(self, ctx:FirebirdParser.Resource_parametersContext):
        pass

    # Exit a parse tree produced by FirebirdParser#resource_parameters.
    def exitResource_parameters(self, ctx:FirebirdParser.Resource_parametersContext):
        pass


    # Enter a parse tree produced by FirebirdParser#password_parameters.
    def enterPassword_parameters(self, ctx:FirebirdParser.Password_parametersContext):
        pass

    # Exit a parse tree produced by FirebirdParser#password_parameters.
    def exitPassword_parameters(self, ctx:FirebirdParser.Password_parametersContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_lockdown_profile.
    def enterCreate_lockdown_profile(self, ctx:FirebirdParser.Create_lockdown_profileContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_lockdown_profile.
    def exitCreate_lockdown_profile(self, ctx:FirebirdParser.Create_lockdown_profileContext):
        pass


    # Enter a parse tree produced by FirebirdParser#static_base_profile.
    def enterStatic_base_profile(self, ctx:FirebirdParser.Static_base_profileContext):
        pass

    # Exit a parse tree produced by FirebirdParser#static_base_profile.
    def exitStatic_base_profile(self, ctx:FirebirdParser.Static_base_profileContext):
        pass


    # Enter a parse tree produced by FirebirdParser#dynamic_base_profile.
    def enterDynamic_base_profile(self, ctx:FirebirdParser.Dynamic_base_profileContext):
        pass

    # Exit a parse tree produced by FirebirdParser#dynamic_base_profile.
    def exitDynamic_base_profile(self, ctx:FirebirdParser.Dynamic_base_profileContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_outline.
    def enterCreate_outline(self, ctx:FirebirdParser.Create_outlineContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_outline.
    def exitCreate_outline(self, ctx:FirebirdParser.Create_outlineContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_restore_point.
    def enterCreate_restore_point(self, ctx:FirebirdParser.Create_restore_pointContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_restore_point.
    def exitCreate_restore_point(self, ctx:FirebirdParser.Create_restore_pointContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_role.
    def enterCreate_role(self, ctx:FirebirdParser.Create_roleContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_role.
    def exitCreate_role(self, ctx:FirebirdParser.Create_roleContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_table.
    def enterCreate_table(self, ctx:FirebirdParser.Create_tableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_table.
    def exitCreate_table(self, ctx:FirebirdParser.Create_tableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xmltype_table.
    def enterXmltype_table(self, ctx:FirebirdParser.Xmltype_tableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xmltype_table.
    def exitXmltype_table(self, ctx:FirebirdParser.Xmltype_tableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xmltype_virtual_columns.
    def enterXmltype_virtual_columns(self, ctx:FirebirdParser.Xmltype_virtual_columnsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xmltype_virtual_columns.
    def exitXmltype_virtual_columns(self, ctx:FirebirdParser.Xmltype_virtual_columnsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xmltype_column_properties.
    def enterXmltype_column_properties(self, ctx:FirebirdParser.Xmltype_column_propertiesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xmltype_column_properties.
    def exitXmltype_column_properties(self, ctx:FirebirdParser.Xmltype_column_propertiesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xmltype_storage.
    def enterXmltype_storage(self, ctx:FirebirdParser.Xmltype_storageContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xmltype_storage.
    def exitXmltype_storage(self, ctx:FirebirdParser.Xmltype_storageContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xmlschema_spec.
    def enterXmlschema_spec(self, ctx:FirebirdParser.Xmlschema_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xmlschema_spec.
    def exitXmlschema_spec(self, ctx:FirebirdParser.Xmlschema_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#object_table.
    def enterObject_table(self, ctx:FirebirdParser.Object_tableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#object_table.
    def exitObject_table(self, ctx:FirebirdParser.Object_tableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#object_type.
    def enterObject_type(self, ctx:FirebirdParser.Object_typeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#object_type.
    def exitObject_type(self, ctx:FirebirdParser.Object_typeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#oid_index_clause.
    def enterOid_index_clause(self, ctx:FirebirdParser.Oid_index_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#oid_index_clause.
    def exitOid_index_clause(self, ctx:FirebirdParser.Oid_index_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#oid_clause.
    def enterOid_clause(self, ctx:FirebirdParser.Oid_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#oid_clause.
    def exitOid_clause(self, ctx:FirebirdParser.Oid_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#object_properties.
    def enterObject_properties(self, ctx:FirebirdParser.Object_propertiesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#object_properties.
    def exitObject_properties(self, ctx:FirebirdParser.Object_propertiesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#object_table_substitution.
    def enterObject_table_substitution(self, ctx:FirebirdParser.Object_table_substitutionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#object_table_substitution.
    def exitObject_table_substitution(self, ctx:FirebirdParser.Object_table_substitutionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#relational_table.
    def enterRelational_table(self, ctx:FirebirdParser.Relational_tableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#relational_table.
    def exitRelational_table(self, ctx:FirebirdParser.Relational_tableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#relational_table_properties.
    def enterRelational_table_properties(self, ctx:FirebirdParser.Relational_table_propertiesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#relational_table_properties.
    def exitRelational_table_properties(self, ctx:FirebirdParser.Relational_table_propertiesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#relational_table_property.
    def enterRelational_table_property(self, ctx:FirebirdParser.Relational_table_propertyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#relational_table_property.
    def exitRelational_table_property(self, ctx:FirebirdParser.Relational_table_propertyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#immutable_table_clauses.
    def enterImmutable_table_clauses(self, ctx:FirebirdParser.Immutable_table_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#immutable_table_clauses.
    def exitImmutable_table_clauses(self, ctx:FirebirdParser.Immutable_table_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#immutable_table_no_drop_clause.
    def enterImmutable_table_no_drop_clause(self, ctx:FirebirdParser.Immutable_table_no_drop_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#immutable_table_no_drop_clause.
    def exitImmutable_table_no_drop_clause(self, ctx:FirebirdParser.Immutable_table_no_drop_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#immutable_table_no_delete_clause.
    def enterImmutable_table_no_delete_clause(self, ctx:FirebirdParser.Immutable_table_no_delete_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#immutable_table_no_delete_clause.
    def exitImmutable_table_no_delete_clause(self, ctx:FirebirdParser.Immutable_table_no_delete_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#blockchain_table_clauses.
    def enterBlockchain_table_clauses(self, ctx:FirebirdParser.Blockchain_table_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#blockchain_table_clauses.
    def exitBlockchain_table_clauses(self, ctx:FirebirdParser.Blockchain_table_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#blockchain_drop_table_clause.
    def enterBlockchain_drop_table_clause(self, ctx:FirebirdParser.Blockchain_drop_table_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#blockchain_drop_table_clause.
    def exitBlockchain_drop_table_clause(self, ctx:FirebirdParser.Blockchain_drop_table_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#blockchain_row_retention_clause.
    def enterBlockchain_row_retention_clause(self, ctx:FirebirdParser.Blockchain_row_retention_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#blockchain_row_retention_clause.
    def exitBlockchain_row_retention_clause(self, ctx:FirebirdParser.Blockchain_row_retention_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#blockchain_hash_and_data_format_clause.
    def enterBlockchain_hash_and_data_format_clause(self, ctx:FirebirdParser.Blockchain_hash_and_data_format_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#blockchain_hash_and_data_format_clause.
    def exitBlockchain_hash_and_data_format_clause(self, ctx:FirebirdParser.Blockchain_hash_and_data_format_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#collation_name.
    def enterCollation_name(self, ctx:FirebirdParser.Collation_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#collation_name.
    def exitCollation_name(self, ctx:FirebirdParser.Collation_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#table_properties.
    def enterTable_properties(self, ctx:FirebirdParser.Table_propertiesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#table_properties.
    def exitTable_properties(self, ctx:FirebirdParser.Table_propertiesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#read_only_clause.
    def enterRead_only_clause(self, ctx:FirebirdParser.Read_only_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#read_only_clause.
    def exitRead_only_clause(self, ctx:FirebirdParser.Read_only_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#indexing_clause.
    def enterIndexing_clause(self, ctx:FirebirdParser.Indexing_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#indexing_clause.
    def exitIndexing_clause(self, ctx:FirebirdParser.Indexing_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#attribute_clustering_clause.
    def enterAttribute_clustering_clause(self, ctx:FirebirdParser.Attribute_clustering_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#attribute_clustering_clause.
    def exitAttribute_clustering_clause(self, ctx:FirebirdParser.Attribute_clustering_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#clustering_join.
    def enterClustering_join(self, ctx:FirebirdParser.Clustering_joinContext):
        pass

    # Exit a parse tree produced by FirebirdParser#clustering_join.
    def exitClustering_join(self, ctx:FirebirdParser.Clustering_joinContext):
        pass


    # Enter a parse tree produced by FirebirdParser#clustering_join_item.
    def enterClustering_join_item(self, ctx:FirebirdParser.Clustering_join_itemContext):
        pass

    # Exit a parse tree produced by FirebirdParser#clustering_join_item.
    def exitClustering_join_item(self, ctx:FirebirdParser.Clustering_join_itemContext):
        pass


    # Enter a parse tree produced by FirebirdParser#equijoin_condition.
    def enterEquijoin_condition(self, ctx:FirebirdParser.Equijoin_conditionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#equijoin_condition.
    def exitEquijoin_condition(self, ctx:FirebirdParser.Equijoin_conditionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#cluster_clause.
    def enterCluster_clause(self, ctx:FirebirdParser.Cluster_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#cluster_clause.
    def exitCluster_clause(self, ctx:FirebirdParser.Cluster_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#clustering_columns.
    def enterClustering_columns(self, ctx:FirebirdParser.Clustering_columnsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#clustering_columns.
    def exitClustering_columns(self, ctx:FirebirdParser.Clustering_columnsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#clustering_column_group.
    def enterClustering_column_group(self, ctx:FirebirdParser.Clustering_column_groupContext):
        pass

    # Exit a parse tree produced by FirebirdParser#clustering_column_group.
    def exitClustering_column_group(self, ctx:FirebirdParser.Clustering_column_groupContext):
        pass


    # Enter a parse tree produced by FirebirdParser#yes_no.
    def enterYes_no(self, ctx:FirebirdParser.Yes_noContext):
        pass

    # Exit a parse tree produced by FirebirdParser#yes_no.
    def exitYes_no(self, ctx:FirebirdParser.Yes_noContext):
        pass


    # Enter a parse tree produced by FirebirdParser#zonemap_clause.
    def enterZonemap_clause(self, ctx:FirebirdParser.Zonemap_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#zonemap_clause.
    def exitZonemap_clause(self, ctx:FirebirdParser.Zonemap_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#logical_replication_clause.
    def enterLogical_replication_clause(self, ctx:FirebirdParser.Logical_replication_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#logical_replication_clause.
    def exitLogical_replication_clause(self, ctx:FirebirdParser.Logical_replication_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#table_name.
    def enterTable_name(self, ctx:FirebirdParser.Table_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#table_name.
    def exitTable_name(self, ctx:FirebirdParser.Table_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#relational_property.
    def enterRelational_property(self, ctx:FirebirdParser.Relational_propertyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#relational_property.
    def exitRelational_property(self, ctx:FirebirdParser.Relational_propertyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#table_partitioning_clauses.
    def enterTable_partitioning_clauses(self, ctx:FirebirdParser.Table_partitioning_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#table_partitioning_clauses.
    def exitTable_partitioning_clauses(self, ctx:FirebirdParser.Table_partitioning_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#range_partitions.
    def enterRange_partitions(self, ctx:FirebirdParser.Range_partitionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#range_partitions.
    def exitRange_partitions(self, ctx:FirebirdParser.Range_partitionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#list_partitions.
    def enterList_partitions(self, ctx:FirebirdParser.List_partitionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#list_partitions.
    def exitList_partitions(self, ctx:FirebirdParser.List_partitionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#hash_partitions.
    def enterHash_partitions(self, ctx:FirebirdParser.Hash_partitionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#hash_partitions.
    def exitHash_partitions(self, ctx:FirebirdParser.Hash_partitionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#individual_hash_partitions.
    def enterIndividual_hash_partitions(self, ctx:FirebirdParser.Individual_hash_partitionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#individual_hash_partitions.
    def exitIndividual_hash_partitions(self, ctx:FirebirdParser.Individual_hash_partitionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#hash_partitions_by_quantity.
    def enterHash_partitions_by_quantity(self, ctx:FirebirdParser.Hash_partitions_by_quantityContext):
        pass

    # Exit a parse tree produced by FirebirdParser#hash_partitions_by_quantity.
    def exitHash_partitions_by_quantity(self, ctx:FirebirdParser.Hash_partitions_by_quantityContext):
        pass


    # Enter a parse tree produced by FirebirdParser#hash_partition_quantity.
    def enterHash_partition_quantity(self, ctx:FirebirdParser.Hash_partition_quantityContext):
        pass

    # Exit a parse tree produced by FirebirdParser#hash_partition_quantity.
    def exitHash_partition_quantity(self, ctx:FirebirdParser.Hash_partition_quantityContext):
        pass


    # Enter a parse tree produced by FirebirdParser#composite_range_partitions.
    def enterComposite_range_partitions(self, ctx:FirebirdParser.Composite_range_partitionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#composite_range_partitions.
    def exitComposite_range_partitions(self, ctx:FirebirdParser.Composite_range_partitionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#composite_list_partitions.
    def enterComposite_list_partitions(self, ctx:FirebirdParser.Composite_list_partitionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#composite_list_partitions.
    def exitComposite_list_partitions(self, ctx:FirebirdParser.Composite_list_partitionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#composite_hash_partitions.
    def enterComposite_hash_partitions(self, ctx:FirebirdParser.Composite_hash_partitionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#composite_hash_partitions.
    def exitComposite_hash_partitions(self, ctx:FirebirdParser.Composite_hash_partitionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#reference_partitioning.
    def enterReference_partitioning(self, ctx:FirebirdParser.Reference_partitioningContext):
        pass

    # Exit a parse tree produced by FirebirdParser#reference_partitioning.
    def exitReference_partitioning(self, ctx:FirebirdParser.Reference_partitioningContext):
        pass


    # Enter a parse tree produced by FirebirdParser#reference_partition_desc.
    def enterReference_partition_desc(self, ctx:FirebirdParser.Reference_partition_descContext):
        pass

    # Exit a parse tree produced by FirebirdParser#reference_partition_desc.
    def exitReference_partition_desc(self, ctx:FirebirdParser.Reference_partition_descContext):
        pass


    # Enter a parse tree produced by FirebirdParser#system_partitioning.
    def enterSystem_partitioning(self, ctx:FirebirdParser.System_partitioningContext):
        pass

    # Exit a parse tree produced by FirebirdParser#system_partitioning.
    def exitSystem_partitioning(self, ctx:FirebirdParser.System_partitioningContext):
        pass


    # Enter a parse tree produced by FirebirdParser#range_partition_desc.
    def enterRange_partition_desc(self, ctx:FirebirdParser.Range_partition_descContext):
        pass

    # Exit a parse tree produced by FirebirdParser#range_partition_desc.
    def exitRange_partition_desc(self, ctx:FirebirdParser.Range_partition_descContext):
        pass


    # Enter a parse tree produced by FirebirdParser#list_partition_desc.
    def enterList_partition_desc(self, ctx:FirebirdParser.List_partition_descContext):
        pass

    # Exit a parse tree produced by FirebirdParser#list_partition_desc.
    def exitList_partition_desc(self, ctx:FirebirdParser.List_partition_descContext):
        pass


    # Enter a parse tree produced by FirebirdParser#subpartition_template.
    def enterSubpartition_template(self, ctx:FirebirdParser.Subpartition_templateContext):
        pass

    # Exit a parse tree produced by FirebirdParser#subpartition_template.
    def exitSubpartition_template(self, ctx:FirebirdParser.Subpartition_templateContext):
        pass


    # Enter a parse tree produced by FirebirdParser#hash_subpartition_quantity.
    def enterHash_subpartition_quantity(self, ctx:FirebirdParser.Hash_subpartition_quantityContext):
        pass

    # Exit a parse tree produced by FirebirdParser#hash_subpartition_quantity.
    def exitHash_subpartition_quantity(self, ctx:FirebirdParser.Hash_subpartition_quantityContext):
        pass


    # Enter a parse tree produced by FirebirdParser#subpartition_by_range.
    def enterSubpartition_by_range(self, ctx:FirebirdParser.Subpartition_by_rangeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#subpartition_by_range.
    def exitSubpartition_by_range(self, ctx:FirebirdParser.Subpartition_by_rangeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#subpartition_by_list.
    def enterSubpartition_by_list(self, ctx:FirebirdParser.Subpartition_by_listContext):
        pass

    # Exit a parse tree produced by FirebirdParser#subpartition_by_list.
    def exitSubpartition_by_list(self, ctx:FirebirdParser.Subpartition_by_listContext):
        pass


    # Enter a parse tree produced by FirebirdParser#subpartition_by_hash.
    def enterSubpartition_by_hash(self, ctx:FirebirdParser.Subpartition_by_hashContext):
        pass

    # Exit a parse tree produced by FirebirdParser#subpartition_by_hash.
    def exitSubpartition_by_hash(self, ctx:FirebirdParser.Subpartition_by_hashContext):
        pass


    # Enter a parse tree produced by FirebirdParser#subpartition_name.
    def enterSubpartition_name(self, ctx:FirebirdParser.Subpartition_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#subpartition_name.
    def exitSubpartition_name(self, ctx:FirebirdParser.Subpartition_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#range_subpartition_desc.
    def enterRange_subpartition_desc(self, ctx:FirebirdParser.Range_subpartition_descContext):
        pass

    # Exit a parse tree produced by FirebirdParser#range_subpartition_desc.
    def exitRange_subpartition_desc(self, ctx:FirebirdParser.Range_subpartition_descContext):
        pass


    # Enter a parse tree produced by FirebirdParser#list_subpartition_desc.
    def enterList_subpartition_desc(self, ctx:FirebirdParser.List_subpartition_descContext):
        pass

    # Exit a parse tree produced by FirebirdParser#list_subpartition_desc.
    def exitList_subpartition_desc(self, ctx:FirebirdParser.List_subpartition_descContext):
        pass


    # Enter a parse tree produced by FirebirdParser#individual_hash_subparts.
    def enterIndividual_hash_subparts(self, ctx:FirebirdParser.Individual_hash_subpartsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#individual_hash_subparts.
    def exitIndividual_hash_subparts(self, ctx:FirebirdParser.Individual_hash_subpartsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#hash_subparts_by_quantity.
    def enterHash_subparts_by_quantity(self, ctx:FirebirdParser.Hash_subparts_by_quantityContext):
        pass

    # Exit a parse tree produced by FirebirdParser#hash_subparts_by_quantity.
    def exitHash_subparts_by_quantity(self, ctx:FirebirdParser.Hash_subparts_by_quantityContext):
        pass


    # Enter a parse tree produced by FirebirdParser#range_values_clause.
    def enterRange_values_clause(self, ctx:FirebirdParser.Range_values_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#range_values_clause.
    def exitRange_values_clause(self, ctx:FirebirdParser.Range_values_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#range_values_list.
    def enterRange_values_list(self, ctx:FirebirdParser.Range_values_listContext):
        pass

    # Exit a parse tree produced by FirebirdParser#range_values_list.
    def exitRange_values_list(self, ctx:FirebirdParser.Range_values_listContext):
        pass


    # Enter a parse tree produced by FirebirdParser#list_values_clause.
    def enterList_values_clause(self, ctx:FirebirdParser.List_values_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#list_values_clause.
    def exitList_values_clause(self, ctx:FirebirdParser.List_values_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#table_partition_description.
    def enterTable_partition_description(self, ctx:FirebirdParser.Table_partition_descriptionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#table_partition_description.
    def exitTable_partition_description(self, ctx:FirebirdParser.Table_partition_descriptionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#partitioning_storage_clause.
    def enterPartitioning_storage_clause(self, ctx:FirebirdParser.Partitioning_storage_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#partitioning_storage_clause.
    def exitPartitioning_storage_clause(self, ctx:FirebirdParser.Partitioning_storage_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lob_partitioning_storage.
    def enterLob_partitioning_storage(self, ctx:FirebirdParser.Lob_partitioning_storageContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lob_partitioning_storage.
    def exitLob_partitioning_storage(self, ctx:FirebirdParser.Lob_partitioning_storageContext):
        pass


    # Enter a parse tree produced by FirebirdParser#size_clause.
    def enterSize_clause(self, ctx:FirebirdParser.Size_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#size_clause.
    def exitSize_clause(self, ctx:FirebirdParser.Size_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#table_compression.
    def enterTable_compression(self, ctx:FirebirdParser.Table_compressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#table_compression.
    def exitTable_compression(self, ctx:FirebirdParser.Table_compressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#inmemory_table_clause.
    def enterInmemory_table_clause(self, ctx:FirebirdParser.Inmemory_table_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#inmemory_table_clause.
    def exitInmemory_table_clause(self, ctx:FirebirdParser.Inmemory_table_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#inmemory_attributes.
    def enterInmemory_attributes(self, ctx:FirebirdParser.Inmemory_attributesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#inmemory_attributes.
    def exitInmemory_attributes(self, ctx:FirebirdParser.Inmemory_attributesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#inmemory_memcompress.
    def enterInmemory_memcompress(self, ctx:FirebirdParser.Inmemory_memcompressContext):
        pass

    # Exit a parse tree produced by FirebirdParser#inmemory_memcompress.
    def exitInmemory_memcompress(self, ctx:FirebirdParser.Inmemory_memcompressContext):
        pass


    # Enter a parse tree produced by FirebirdParser#inmemory_priority.
    def enterInmemory_priority(self, ctx:FirebirdParser.Inmemory_priorityContext):
        pass

    # Exit a parse tree produced by FirebirdParser#inmemory_priority.
    def exitInmemory_priority(self, ctx:FirebirdParser.Inmemory_priorityContext):
        pass


    # Enter a parse tree produced by FirebirdParser#inmemory_distribute.
    def enterInmemory_distribute(self, ctx:FirebirdParser.Inmemory_distributeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#inmemory_distribute.
    def exitInmemory_distribute(self, ctx:FirebirdParser.Inmemory_distributeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#inmemory_duplicate.
    def enterInmemory_duplicate(self, ctx:FirebirdParser.Inmemory_duplicateContext):
        pass

    # Exit a parse tree produced by FirebirdParser#inmemory_duplicate.
    def exitInmemory_duplicate(self, ctx:FirebirdParser.Inmemory_duplicateContext):
        pass


    # Enter a parse tree produced by FirebirdParser#inmemory_column_clause.
    def enterInmemory_column_clause(self, ctx:FirebirdParser.Inmemory_column_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#inmemory_column_clause.
    def exitInmemory_column_clause(self, ctx:FirebirdParser.Inmemory_column_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#physical_attributes_clause.
    def enterPhysical_attributes_clause(self, ctx:FirebirdParser.Physical_attributes_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#physical_attributes_clause.
    def exitPhysical_attributes_clause(self, ctx:FirebirdParser.Physical_attributes_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#storage_clause.
    def enterStorage_clause(self, ctx:FirebirdParser.Storage_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#storage_clause.
    def exitStorage_clause(self, ctx:FirebirdParser.Storage_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#deferred_segment_creation.
    def enterDeferred_segment_creation(self, ctx:FirebirdParser.Deferred_segment_creationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#deferred_segment_creation.
    def exitDeferred_segment_creation(self, ctx:FirebirdParser.Deferred_segment_creationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#segment_attributes_clause.
    def enterSegment_attributes_clause(self, ctx:FirebirdParser.Segment_attributes_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#segment_attributes_clause.
    def exitSegment_attributes_clause(self, ctx:FirebirdParser.Segment_attributes_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#physical_properties.
    def enterPhysical_properties(self, ctx:FirebirdParser.Physical_propertiesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#physical_properties.
    def exitPhysical_properties(self, ctx:FirebirdParser.Physical_propertiesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#ilm_clause.
    def enterIlm_clause(self, ctx:FirebirdParser.Ilm_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#ilm_clause.
    def exitIlm_clause(self, ctx:FirebirdParser.Ilm_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#ilm_policy_clause.
    def enterIlm_policy_clause(self, ctx:FirebirdParser.Ilm_policy_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#ilm_policy_clause.
    def exitIlm_policy_clause(self, ctx:FirebirdParser.Ilm_policy_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#ilm_compression_policy.
    def enterIlm_compression_policy(self, ctx:FirebirdParser.Ilm_compression_policyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#ilm_compression_policy.
    def exitIlm_compression_policy(self, ctx:FirebirdParser.Ilm_compression_policyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#ilm_tiering_policy.
    def enterIlm_tiering_policy(self, ctx:FirebirdParser.Ilm_tiering_policyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#ilm_tiering_policy.
    def exitIlm_tiering_policy(self, ctx:FirebirdParser.Ilm_tiering_policyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#ilm_after_on.
    def enterIlm_after_on(self, ctx:FirebirdParser.Ilm_after_onContext):
        pass

    # Exit a parse tree produced by FirebirdParser#ilm_after_on.
    def exitIlm_after_on(self, ctx:FirebirdParser.Ilm_after_onContext):
        pass


    # Enter a parse tree produced by FirebirdParser#segment_group.
    def enterSegment_group(self, ctx:FirebirdParser.Segment_groupContext):
        pass

    # Exit a parse tree produced by FirebirdParser#segment_group.
    def exitSegment_group(self, ctx:FirebirdParser.Segment_groupContext):
        pass


    # Enter a parse tree produced by FirebirdParser#ilm_inmemory_policy.
    def enterIlm_inmemory_policy(self, ctx:FirebirdParser.Ilm_inmemory_policyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#ilm_inmemory_policy.
    def exitIlm_inmemory_policy(self, ctx:FirebirdParser.Ilm_inmemory_policyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#ilm_time_period.
    def enterIlm_time_period(self, ctx:FirebirdParser.Ilm_time_periodContext):
        pass

    # Exit a parse tree produced by FirebirdParser#ilm_time_period.
    def exitIlm_time_period(self, ctx:FirebirdParser.Ilm_time_periodContext):
        pass


    # Enter a parse tree produced by FirebirdParser#heap_org_table_clause.
    def enterHeap_org_table_clause(self, ctx:FirebirdParser.Heap_org_table_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#heap_org_table_clause.
    def exitHeap_org_table_clause(self, ctx:FirebirdParser.Heap_org_table_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_clause.
    def enterExternal_table_clause(self, ctx:FirebirdParser.External_table_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_clause.
    def exitExternal_table_clause(self, ctx:FirebirdParser.External_table_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#access_driver_type.
    def enterAccess_driver_type(self, ctx:FirebirdParser.Access_driver_typeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#access_driver_type.
    def exitAccess_driver_type(self, ctx:FirebirdParser.Access_driver_typeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_data_props.
    def enterExternal_table_data_props(self, ctx:FirebirdParser.External_table_data_propsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_data_props.
    def exitExternal_table_data_props(self, ctx:FirebirdParser.External_table_data_propsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_data_format.
    def enterExternal_table_data_format(self, ctx:FirebirdParser.External_table_data_formatContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_data_format.
    def exitExternal_table_data_format(self, ctx:FirebirdParser.External_table_data_formatContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_transform.
    def enterExternal_table_transform(self, ctx:FirebirdParser.External_table_transformContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_transform.
    def exitExternal_table_transform(self, ctx:FirebirdParser.External_table_transformContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_field.
    def enterExternal_table_field(self, ctx:FirebirdParser.External_table_fieldContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_field.
    def exitExternal_table_field(self, ctx:FirebirdParser.External_table_fieldContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_field_list.
    def enterExternal_table_field_list(self, ctx:FirebirdParser.External_table_field_listContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_field_list.
    def exitExternal_table_field_list(self, ctx:FirebirdParser.External_table_field_listContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_fields_clause.
    def enterExternal_table_fields_clause(self, ctx:FirebirdParser.External_table_fields_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_fields_clause.
    def exitExternal_table_fields_clause(self, ctx:FirebirdParser.External_table_fields_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_position_clause.
    def enterExternal_table_position_clause(self, ctx:FirebirdParser.External_table_position_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_position_clause.
    def exitExternal_table_position_clause(self, ctx:FirebirdParser.External_table_position_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_datatype_clause.
    def enterExternal_table_datatype_clause(self, ctx:FirebirdParser.External_table_datatype_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_datatype_clause.
    def exitExternal_table_datatype_clause(self, ctx:FirebirdParser.External_table_datatype_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_delimit_clause.
    def enterExternal_table_delimit_clause(self, ctx:FirebirdParser.External_table_delimit_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_delimit_clause.
    def exitExternal_table_delimit_clause(self, ctx:FirebirdParser.External_table_delimit_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_trim_clause.
    def enterExternal_table_trim_clause(self, ctx:FirebirdParser.External_table_trim_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_trim_clause.
    def exitExternal_table_trim_clause(self, ctx:FirebirdParser.External_table_trim_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_date_format_clause.
    def enterExternal_table_date_format_clause(self, ctx:FirebirdParser.External_table_date_format_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_date_format_clause.
    def exitExternal_table_date_format_clause(self, ctx:FirebirdParser.External_table_date_format_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_init_clause.
    def enterExternal_table_init_clause(self, ctx:FirebirdParser.External_table_init_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_init_clause.
    def exitExternal_table_init_clause(self, ctx:FirebirdParser.External_table_init_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_condition_clause.
    def enterExternal_table_condition_clause(self, ctx:FirebirdParser.External_table_condition_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_condition_clause.
    def exitExternal_table_condition_clause(self, ctx:FirebirdParser.External_table_condition_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_lls_clause.
    def enterExternal_table_lls_clause(self, ctx:FirebirdParser.External_table_lls_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_lls_clause.
    def exitExternal_table_lls_clause(self, ctx:FirebirdParser.External_table_lls_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_records.
    def enterExternal_table_records(self, ctx:FirebirdParser.External_table_recordsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_records.
    def exitExternal_table_records(self, ctx:FirebirdParser.External_table_recordsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_record_options_clause.
    def enterExternal_table_record_options_clause(self, ctx:FirebirdParser.External_table_record_options_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_record_options_clause.
    def exitExternal_table_record_options_clause(self, ctx:FirebirdParser.External_table_record_options_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_output_files.
    def enterExternal_table_output_files(self, ctx:FirebirdParser.External_table_output_filesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_output_files.
    def exitExternal_table_output_files(self, ctx:FirebirdParser.External_table_output_filesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_fields.
    def enterExternal_table_fields(self, ctx:FirebirdParser.External_table_fieldsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_fields.
    def exitExternal_table_fields(self, ctx:FirebirdParser.External_table_fieldsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_datapump.
    def enterExternal_table_datapump(self, ctx:FirebirdParser.External_table_datapumpContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_datapump.
    def exitExternal_table_datapump(self, ctx:FirebirdParser.External_table_datapumpContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_hive.
    def enterExternal_table_hive(self, ctx:FirebirdParser.External_table_hiveContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_hive.
    def exitExternal_table_hive(self, ctx:FirebirdParser.External_table_hiveContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_hive_parameter_map.
    def enterExternal_table_hive_parameter_map(self, ctx:FirebirdParser.External_table_hive_parameter_mapContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_hive_parameter_map.
    def exitExternal_table_hive_parameter_map(self, ctx:FirebirdParser.External_table_hive_parameter_mapContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_hive_parameter_map_entry.
    def enterExternal_table_hive_parameter_map_entry(self, ctx:FirebirdParser.External_table_hive_parameter_map_entryContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_hive_parameter_map_entry.
    def exitExternal_table_hive_parameter_map_entry(self, ctx:FirebirdParser.External_table_hive_parameter_map_entryContext):
        pass


    # Enter a parse tree produced by FirebirdParser#external_table_directory.
    def enterExternal_table_directory(self, ctx:FirebirdParser.External_table_directoryContext):
        pass

    # Exit a parse tree produced by FirebirdParser#external_table_directory.
    def exitExternal_table_directory(self, ctx:FirebirdParser.External_table_directoryContext):
        pass


    # Enter a parse tree produced by FirebirdParser#row_movement_clause.
    def enterRow_movement_clause(self, ctx:FirebirdParser.Row_movement_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#row_movement_clause.
    def exitRow_movement_clause(self, ctx:FirebirdParser.Row_movement_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#flashback_archive_clause.
    def enterFlashback_archive_clause(self, ctx:FirebirdParser.Flashback_archive_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#flashback_archive_clause.
    def exitFlashback_archive_clause(self, ctx:FirebirdParser.Flashback_archive_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#log_grp.
    def enterLog_grp(self, ctx:FirebirdParser.Log_grpContext):
        pass

    # Exit a parse tree produced by FirebirdParser#log_grp.
    def exitLog_grp(self, ctx:FirebirdParser.Log_grpContext):
        pass


    # Enter a parse tree produced by FirebirdParser#supplemental_table_logging.
    def enterSupplemental_table_logging(self, ctx:FirebirdParser.Supplemental_table_loggingContext):
        pass

    # Exit a parse tree produced by FirebirdParser#supplemental_table_logging.
    def exitSupplemental_table_logging(self, ctx:FirebirdParser.Supplemental_table_loggingContext):
        pass


    # Enter a parse tree produced by FirebirdParser#supplemental_log_grp_clause.
    def enterSupplemental_log_grp_clause(self, ctx:FirebirdParser.Supplemental_log_grp_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#supplemental_log_grp_clause.
    def exitSupplemental_log_grp_clause(self, ctx:FirebirdParser.Supplemental_log_grp_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#supplemental_id_key_clause.
    def enterSupplemental_id_key_clause(self, ctx:FirebirdParser.Supplemental_id_key_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#supplemental_id_key_clause.
    def exitSupplemental_id_key_clause(self, ctx:FirebirdParser.Supplemental_id_key_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#allocate_extent_clause.
    def enterAllocate_extent_clause(self, ctx:FirebirdParser.Allocate_extent_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#allocate_extent_clause.
    def exitAllocate_extent_clause(self, ctx:FirebirdParser.Allocate_extent_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#deallocate_unused_clause.
    def enterDeallocate_unused_clause(self, ctx:FirebirdParser.Deallocate_unused_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#deallocate_unused_clause.
    def exitDeallocate_unused_clause(self, ctx:FirebirdParser.Deallocate_unused_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#shrink_clause.
    def enterShrink_clause(self, ctx:FirebirdParser.Shrink_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#shrink_clause.
    def exitShrink_clause(self, ctx:FirebirdParser.Shrink_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#records_per_block_clause.
    def enterRecords_per_block_clause(self, ctx:FirebirdParser.Records_per_block_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#records_per_block_clause.
    def exitRecords_per_block_clause(self, ctx:FirebirdParser.Records_per_block_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#upgrade_table_clause.
    def enterUpgrade_table_clause(self, ctx:FirebirdParser.Upgrade_table_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#upgrade_table_clause.
    def exitUpgrade_table_clause(self, ctx:FirebirdParser.Upgrade_table_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#truncate_table.
    def enterTruncate_table(self, ctx:FirebirdParser.Truncate_tableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#truncate_table.
    def exitTruncate_table(self, ctx:FirebirdParser.Truncate_tableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_table.
    def enterDrop_table(self, ctx:FirebirdParser.Drop_tableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_table.
    def exitDrop_table(self, ctx:FirebirdParser.Drop_tableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_tablespace.
    def enterDrop_tablespace(self, ctx:FirebirdParser.Drop_tablespaceContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_tablespace.
    def exitDrop_tablespace(self, ctx:FirebirdParser.Drop_tablespaceContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_tablespace_set.
    def enterDrop_tablespace_set(self, ctx:FirebirdParser.Drop_tablespace_setContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_tablespace_set.
    def exitDrop_tablespace_set(self, ctx:FirebirdParser.Drop_tablespace_setContext):
        pass


    # Enter a parse tree produced by FirebirdParser#including_contents_clause.
    def enterIncluding_contents_clause(self, ctx:FirebirdParser.Including_contents_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#including_contents_clause.
    def exitIncluding_contents_clause(self, ctx:FirebirdParser.Including_contents_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_view.
    def enterDrop_view(self, ctx:FirebirdParser.Drop_viewContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_view.
    def exitDrop_view(self, ctx:FirebirdParser.Drop_viewContext):
        pass


    # Enter a parse tree produced by FirebirdParser#comment_on_column.
    def enterComment_on_column(self, ctx:FirebirdParser.Comment_on_columnContext):
        pass

    # Exit a parse tree produced by FirebirdParser#comment_on_column.
    def exitComment_on_column(self, ctx:FirebirdParser.Comment_on_columnContext):
        pass


    # Enter a parse tree produced by FirebirdParser#enable_or_disable.
    def enterEnable_or_disable(self, ctx:FirebirdParser.Enable_or_disableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#enable_or_disable.
    def exitEnable_or_disable(self, ctx:FirebirdParser.Enable_or_disableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#allow_or_disallow.
    def enterAllow_or_disallow(self, ctx:FirebirdParser.Allow_or_disallowContext):
        pass

    # Exit a parse tree produced by FirebirdParser#allow_or_disallow.
    def exitAllow_or_disallow(self, ctx:FirebirdParser.Allow_or_disallowContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_synonym.
    def enterAlter_synonym(self, ctx:FirebirdParser.Alter_synonymContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_synonym.
    def exitAlter_synonym(self, ctx:FirebirdParser.Alter_synonymContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_synonym.
    def enterCreate_synonym(self, ctx:FirebirdParser.Create_synonymContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_synonym.
    def exitCreate_synonym(self, ctx:FirebirdParser.Create_synonymContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_synonym.
    def enterDrop_synonym(self, ctx:FirebirdParser.Drop_synonymContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_synonym.
    def exitDrop_synonym(self, ctx:FirebirdParser.Drop_synonymContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_spfile.
    def enterCreate_spfile(self, ctx:FirebirdParser.Create_spfileContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_spfile.
    def exitCreate_spfile(self, ctx:FirebirdParser.Create_spfileContext):
        pass


    # Enter a parse tree produced by FirebirdParser#spfile_name.
    def enterSpfile_name(self, ctx:FirebirdParser.Spfile_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#spfile_name.
    def exitSpfile_name(self, ctx:FirebirdParser.Spfile_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#pfile_name.
    def enterPfile_name(self, ctx:FirebirdParser.Pfile_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#pfile_name.
    def exitPfile_name(self, ctx:FirebirdParser.Pfile_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#comment_on_table.
    def enterComment_on_table(self, ctx:FirebirdParser.Comment_on_tableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#comment_on_table.
    def exitComment_on_table(self, ctx:FirebirdParser.Comment_on_tableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#comment_on_materialized.
    def enterComment_on_materialized(self, ctx:FirebirdParser.Comment_on_materializedContext):
        pass

    # Exit a parse tree produced by FirebirdParser#comment_on_materialized.
    def exitComment_on_materialized(self, ctx:FirebirdParser.Comment_on_materializedContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_analytic_view.
    def enterAlter_analytic_view(self, ctx:FirebirdParser.Alter_analytic_viewContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_analytic_view.
    def exitAlter_analytic_view(self, ctx:FirebirdParser.Alter_analytic_viewContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_add_cache_clause.
    def enterAlter_add_cache_clause(self, ctx:FirebirdParser.Alter_add_cache_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_add_cache_clause.
    def exitAlter_add_cache_clause(self, ctx:FirebirdParser.Alter_add_cache_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#levels_item.
    def enterLevels_item(self, ctx:FirebirdParser.Levels_itemContext):
        pass

    # Exit a parse tree produced by FirebirdParser#levels_item.
    def exitLevels_item(self, ctx:FirebirdParser.Levels_itemContext):
        pass


    # Enter a parse tree produced by FirebirdParser#measure_list.
    def enterMeasure_list(self, ctx:FirebirdParser.Measure_listContext):
        pass

    # Exit a parse tree produced by FirebirdParser#measure_list.
    def exitMeasure_list(self, ctx:FirebirdParser.Measure_listContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_drop_cache_clause.
    def enterAlter_drop_cache_clause(self, ctx:FirebirdParser.Alter_drop_cache_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_drop_cache_clause.
    def exitAlter_drop_cache_clause(self, ctx:FirebirdParser.Alter_drop_cache_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_attribute_dimension.
    def enterAlter_attribute_dimension(self, ctx:FirebirdParser.Alter_attribute_dimensionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_attribute_dimension.
    def exitAlter_attribute_dimension(self, ctx:FirebirdParser.Alter_attribute_dimensionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_audit_policy.
    def enterAlter_audit_policy(self, ctx:FirebirdParser.Alter_audit_policyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_audit_policy.
    def exitAlter_audit_policy(self, ctx:FirebirdParser.Alter_audit_policyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_cluster.
    def enterAlter_cluster(self, ctx:FirebirdParser.Alter_clusterContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_cluster.
    def exitAlter_cluster(self, ctx:FirebirdParser.Alter_clusterContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_analytic_view.
    def enterDrop_analytic_view(self, ctx:FirebirdParser.Drop_analytic_viewContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_analytic_view.
    def exitDrop_analytic_view(self, ctx:FirebirdParser.Drop_analytic_viewContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_attribute_dimension.
    def enterDrop_attribute_dimension(self, ctx:FirebirdParser.Drop_attribute_dimensionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_attribute_dimension.
    def exitDrop_attribute_dimension(self, ctx:FirebirdParser.Drop_attribute_dimensionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_audit_policy.
    def enterDrop_audit_policy(self, ctx:FirebirdParser.Drop_audit_policyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_audit_policy.
    def exitDrop_audit_policy(self, ctx:FirebirdParser.Drop_audit_policyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_flashback_archive.
    def enterDrop_flashback_archive(self, ctx:FirebirdParser.Drop_flashback_archiveContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_flashback_archive.
    def exitDrop_flashback_archive(self, ctx:FirebirdParser.Drop_flashback_archiveContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_cluster.
    def enterDrop_cluster(self, ctx:FirebirdParser.Drop_clusterContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_cluster.
    def exitDrop_cluster(self, ctx:FirebirdParser.Drop_clusterContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_context.
    def enterDrop_context(self, ctx:FirebirdParser.Drop_contextContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_context.
    def exitDrop_context(self, ctx:FirebirdParser.Drop_contextContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_directory.
    def enterDrop_directory(self, ctx:FirebirdParser.Drop_directoryContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_directory.
    def exitDrop_directory(self, ctx:FirebirdParser.Drop_directoryContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_diskgroup.
    def enterDrop_diskgroup(self, ctx:FirebirdParser.Drop_diskgroupContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_diskgroup.
    def exitDrop_diskgroup(self, ctx:FirebirdParser.Drop_diskgroupContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_edition.
    def enterDrop_edition(self, ctx:FirebirdParser.Drop_editionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_edition.
    def exitDrop_edition(self, ctx:FirebirdParser.Drop_editionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#truncate_cluster.
    def enterTruncate_cluster(self, ctx:FirebirdParser.Truncate_clusterContext):
        pass

    # Exit a parse tree produced by FirebirdParser#truncate_cluster.
    def exitTruncate_cluster(self, ctx:FirebirdParser.Truncate_clusterContext):
        pass


    # Enter a parse tree produced by FirebirdParser#cache_or_nocache.
    def enterCache_or_nocache(self, ctx:FirebirdParser.Cache_or_nocacheContext):
        pass

    # Exit a parse tree produced by FirebirdParser#cache_or_nocache.
    def exitCache_or_nocache(self, ctx:FirebirdParser.Cache_or_nocacheContext):
        pass


    # Enter a parse tree produced by FirebirdParser#database_name.
    def enterDatabase_name(self, ctx:FirebirdParser.Database_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#database_name.
    def exitDatabase_name(self, ctx:FirebirdParser.Database_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_database.
    def enterAlter_database(self, ctx:FirebirdParser.Alter_databaseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_database.
    def exitAlter_database(self, ctx:FirebirdParser.Alter_databaseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#database_clause.
    def enterDatabase_clause(self, ctx:FirebirdParser.Database_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#database_clause.
    def exitDatabase_clause(self, ctx:FirebirdParser.Database_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#startup_clauses.
    def enterStartup_clauses(self, ctx:FirebirdParser.Startup_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#startup_clauses.
    def exitStartup_clauses(self, ctx:FirebirdParser.Startup_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#resetlogs_or_noresetlogs.
    def enterResetlogs_or_noresetlogs(self, ctx:FirebirdParser.Resetlogs_or_noresetlogsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#resetlogs_or_noresetlogs.
    def exitResetlogs_or_noresetlogs(self, ctx:FirebirdParser.Resetlogs_or_noresetlogsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#upgrade_or_downgrade.
    def enterUpgrade_or_downgrade(self, ctx:FirebirdParser.Upgrade_or_downgradeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#upgrade_or_downgrade.
    def exitUpgrade_or_downgrade(self, ctx:FirebirdParser.Upgrade_or_downgradeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#recovery_clauses.
    def enterRecovery_clauses(self, ctx:FirebirdParser.Recovery_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#recovery_clauses.
    def exitRecovery_clauses(self, ctx:FirebirdParser.Recovery_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#begin_or_end.
    def enterBegin_or_end(self, ctx:FirebirdParser.Begin_or_endContext):
        pass

    # Exit a parse tree produced by FirebirdParser#begin_or_end.
    def exitBegin_or_end(self, ctx:FirebirdParser.Begin_or_endContext):
        pass


    # Enter a parse tree produced by FirebirdParser#general_recovery.
    def enterGeneral_recovery(self, ctx:FirebirdParser.General_recoveryContext):
        pass

    # Exit a parse tree produced by FirebirdParser#general_recovery.
    def exitGeneral_recovery(self, ctx:FirebirdParser.General_recoveryContext):
        pass


    # Enter a parse tree produced by FirebirdParser#full_database_recovery.
    def enterFull_database_recovery(self, ctx:FirebirdParser.Full_database_recoveryContext):
        pass

    # Exit a parse tree produced by FirebirdParser#full_database_recovery.
    def exitFull_database_recovery(self, ctx:FirebirdParser.Full_database_recoveryContext):
        pass


    # Enter a parse tree produced by FirebirdParser#partial_database_recovery.
    def enterPartial_database_recovery(self, ctx:FirebirdParser.Partial_database_recoveryContext):
        pass

    # Exit a parse tree produced by FirebirdParser#partial_database_recovery.
    def exitPartial_database_recovery(self, ctx:FirebirdParser.Partial_database_recoveryContext):
        pass


    # Enter a parse tree produced by FirebirdParser#partial_database_recovery_10g.
    def enterPartial_database_recovery_10g(self, ctx:FirebirdParser.Partial_database_recovery_10gContext):
        pass

    # Exit a parse tree produced by FirebirdParser#partial_database_recovery_10g.
    def exitPartial_database_recovery_10g(self, ctx:FirebirdParser.Partial_database_recovery_10gContext):
        pass


    # Enter a parse tree produced by FirebirdParser#managed_standby_recovery.
    def enterManaged_standby_recovery(self, ctx:FirebirdParser.Managed_standby_recoveryContext):
        pass

    # Exit a parse tree produced by FirebirdParser#managed_standby_recovery.
    def exitManaged_standby_recovery(self, ctx:FirebirdParser.Managed_standby_recoveryContext):
        pass


    # Enter a parse tree produced by FirebirdParser#db_name.
    def enterDb_name(self, ctx:FirebirdParser.Db_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#db_name.
    def exitDb_name(self, ctx:FirebirdParser.Db_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#database_file_clauses.
    def enterDatabase_file_clauses(self, ctx:FirebirdParser.Database_file_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#database_file_clauses.
    def exitDatabase_file_clauses(self, ctx:FirebirdParser.Database_file_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_datafile_clause.
    def enterCreate_datafile_clause(self, ctx:FirebirdParser.Create_datafile_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_datafile_clause.
    def exitCreate_datafile_clause(self, ctx:FirebirdParser.Create_datafile_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_datafile_clause.
    def enterAlter_datafile_clause(self, ctx:FirebirdParser.Alter_datafile_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_datafile_clause.
    def exitAlter_datafile_clause(self, ctx:FirebirdParser.Alter_datafile_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_tempfile_clause.
    def enterAlter_tempfile_clause(self, ctx:FirebirdParser.Alter_tempfile_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_tempfile_clause.
    def exitAlter_tempfile_clause(self, ctx:FirebirdParser.Alter_tempfile_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#move_datafile_clause.
    def enterMove_datafile_clause(self, ctx:FirebirdParser.Move_datafile_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#move_datafile_clause.
    def exitMove_datafile_clause(self, ctx:FirebirdParser.Move_datafile_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#logfile_clauses.
    def enterLogfile_clauses(self, ctx:FirebirdParser.Logfile_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#logfile_clauses.
    def exitLogfile_clauses(self, ctx:FirebirdParser.Logfile_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#add_logfile_clauses.
    def enterAdd_logfile_clauses(self, ctx:FirebirdParser.Add_logfile_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#add_logfile_clauses.
    def exitAdd_logfile_clauses(self, ctx:FirebirdParser.Add_logfile_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#group_redo_logfile.
    def enterGroup_redo_logfile(self, ctx:FirebirdParser.Group_redo_logfileContext):
        pass

    # Exit a parse tree produced by FirebirdParser#group_redo_logfile.
    def exitGroup_redo_logfile(self, ctx:FirebirdParser.Group_redo_logfileContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_logfile_clauses.
    def enterDrop_logfile_clauses(self, ctx:FirebirdParser.Drop_logfile_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_logfile_clauses.
    def exitDrop_logfile_clauses(self, ctx:FirebirdParser.Drop_logfile_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#switch_logfile_clause.
    def enterSwitch_logfile_clause(self, ctx:FirebirdParser.Switch_logfile_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#switch_logfile_clause.
    def exitSwitch_logfile_clause(self, ctx:FirebirdParser.Switch_logfile_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#supplemental_db_logging.
    def enterSupplemental_db_logging(self, ctx:FirebirdParser.Supplemental_db_loggingContext):
        pass

    # Exit a parse tree produced by FirebirdParser#supplemental_db_logging.
    def exitSupplemental_db_logging(self, ctx:FirebirdParser.Supplemental_db_loggingContext):
        pass


    # Enter a parse tree produced by FirebirdParser#add_or_drop.
    def enterAdd_or_drop(self, ctx:FirebirdParser.Add_or_dropContext):
        pass

    # Exit a parse tree produced by FirebirdParser#add_or_drop.
    def exitAdd_or_drop(self, ctx:FirebirdParser.Add_or_dropContext):
        pass


    # Enter a parse tree produced by FirebirdParser#supplemental_plsql_clause.
    def enterSupplemental_plsql_clause(self, ctx:FirebirdParser.Supplemental_plsql_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#supplemental_plsql_clause.
    def exitSupplemental_plsql_clause(self, ctx:FirebirdParser.Supplemental_plsql_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#logfile_descriptor.
    def enterLogfile_descriptor(self, ctx:FirebirdParser.Logfile_descriptorContext):
        pass

    # Exit a parse tree produced by FirebirdParser#logfile_descriptor.
    def exitLogfile_descriptor(self, ctx:FirebirdParser.Logfile_descriptorContext):
        pass


    # Enter a parse tree produced by FirebirdParser#controlfile_clauses.
    def enterControlfile_clauses(self, ctx:FirebirdParser.Controlfile_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#controlfile_clauses.
    def exitControlfile_clauses(self, ctx:FirebirdParser.Controlfile_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#trace_file_clause.
    def enterTrace_file_clause(self, ctx:FirebirdParser.Trace_file_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#trace_file_clause.
    def exitTrace_file_clause(self, ctx:FirebirdParser.Trace_file_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#standby_database_clauses.
    def enterStandby_database_clauses(self, ctx:FirebirdParser.Standby_database_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#standby_database_clauses.
    def exitStandby_database_clauses(self, ctx:FirebirdParser.Standby_database_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#activate_standby_db_clause.
    def enterActivate_standby_db_clause(self, ctx:FirebirdParser.Activate_standby_db_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#activate_standby_db_clause.
    def exitActivate_standby_db_clause(self, ctx:FirebirdParser.Activate_standby_db_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#maximize_standby_db_clause.
    def enterMaximize_standby_db_clause(self, ctx:FirebirdParser.Maximize_standby_db_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#maximize_standby_db_clause.
    def exitMaximize_standby_db_clause(self, ctx:FirebirdParser.Maximize_standby_db_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#register_logfile_clause.
    def enterRegister_logfile_clause(self, ctx:FirebirdParser.Register_logfile_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#register_logfile_clause.
    def exitRegister_logfile_clause(self, ctx:FirebirdParser.Register_logfile_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#commit_switchover_clause.
    def enterCommit_switchover_clause(self, ctx:FirebirdParser.Commit_switchover_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#commit_switchover_clause.
    def exitCommit_switchover_clause(self, ctx:FirebirdParser.Commit_switchover_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#start_standby_clause.
    def enterStart_standby_clause(self, ctx:FirebirdParser.Start_standby_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#start_standby_clause.
    def exitStart_standby_clause(self, ctx:FirebirdParser.Start_standby_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#stop_standby_clause.
    def enterStop_standby_clause(self, ctx:FirebirdParser.Stop_standby_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#stop_standby_clause.
    def exitStop_standby_clause(self, ctx:FirebirdParser.Stop_standby_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#convert_database_clause.
    def enterConvert_database_clause(self, ctx:FirebirdParser.Convert_database_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#convert_database_clause.
    def exitConvert_database_clause(self, ctx:FirebirdParser.Convert_database_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#default_settings_clause.
    def enterDefault_settings_clause(self, ctx:FirebirdParser.Default_settings_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#default_settings_clause.
    def exitDefault_settings_clause(self, ctx:FirebirdParser.Default_settings_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#set_time_zone_clause.
    def enterSet_time_zone_clause(self, ctx:FirebirdParser.Set_time_zone_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#set_time_zone_clause.
    def exitSet_time_zone_clause(self, ctx:FirebirdParser.Set_time_zone_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#instance_clauses.
    def enterInstance_clauses(self, ctx:FirebirdParser.Instance_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#instance_clauses.
    def exitInstance_clauses(self, ctx:FirebirdParser.Instance_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#security_clause.
    def enterSecurity_clause(self, ctx:FirebirdParser.Security_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#security_clause.
    def exitSecurity_clause(self, ctx:FirebirdParser.Security_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#domain.
    def enterDomain(self, ctx:FirebirdParser.DomainContext):
        pass

    # Exit a parse tree produced by FirebirdParser#domain.
    def exitDomain(self, ctx:FirebirdParser.DomainContext):
        pass


    # Enter a parse tree produced by FirebirdParser#database.
    def enterDatabase(self, ctx:FirebirdParser.DatabaseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#database.
    def exitDatabase(self, ctx:FirebirdParser.DatabaseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#edition_name.
    def enterEdition_name(self, ctx:FirebirdParser.Edition_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#edition_name.
    def exitEdition_name(self, ctx:FirebirdParser.Edition_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#filenumber.
    def enterFilenumber(self, ctx:FirebirdParser.FilenumberContext):
        pass

    # Exit a parse tree produced by FirebirdParser#filenumber.
    def exitFilenumber(self, ctx:FirebirdParser.FilenumberContext):
        pass


    # Enter a parse tree produced by FirebirdParser#filename.
    def enterFilename(self, ctx:FirebirdParser.FilenameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#filename.
    def exitFilename(self, ctx:FirebirdParser.FilenameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#prepare_clause.
    def enterPrepare_clause(self, ctx:FirebirdParser.Prepare_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#prepare_clause.
    def exitPrepare_clause(self, ctx:FirebirdParser.Prepare_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_mirror_clause.
    def enterDrop_mirror_clause(self, ctx:FirebirdParser.Drop_mirror_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_mirror_clause.
    def exitDrop_mirror_clause(self, ctx:FirebirdParser.Drop_mirror_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lost_write_protection.
    def enterLost_write_protection(self, ctx:FirebirdParser.Lost_write_protectionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lost_write_protection.
    def exitLost_write_protection(self, ctx:FirebirdParser.Lost_write_protectionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#cdb_fleet_clauses.
    def enterCdb_fleet_clauses(self, ctx:FirebirdParser.Cdb_fleet_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#cdb_fleet_clauses.
    def exitCdb_fleet_clauses(self, ctx:FirebirdParser.Cdb_fleet_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lead_cdb_clause.
    def enterLead_cdb_clause(self, ctx:FirebirdParser.Lead_cdb_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lead_cdb_clause.
    def exitLead_cdb_clause(self, ctx:FirebirdParser.Lead_cdb_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lead_cdb_uri_clause.
    def enterLead_cdb_uri_clause(self, ctx:FirebirdParser.Lead_cdb_uri_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lead_cdb_uri_clause.
    def exitLead_cdb_uri_clause(self, ctx:FirebirdParser.Lead_cdb_uri_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#property_clauses.
    def enterProperty_clauses(self, ctx:FirebirdParser.Property_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#property_clauses.
    def exitProperty_clauses(self, ctx:FirebirdParser.Property_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#replay_upgrade_clauses.
    def enterReplay_upgrade_clauses(self, ctx:FirebirdParser.Replay_upgrade_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#replay_upgrade_clauses.
    def exitReplay_upgrade_clauses(self, ctx:FirebirdParser.Replay_upgrade_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_database_link.
    def enterAlter_database_link(self, ctx:FirebirdParser.Alter_database_linkContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_database_link.
    def exitAlter_database_link(self, ctx:FirebirdParser.Alter_database_linkContext):
        pass


    # Enter a parse tree produced by FirebirdParser#password_value.
    def enterPassword_value(self, ctx:FirebirdParser.Password_valueContext):
        pass

    # Exit a parse tree produced by FirebirdParser#password_value.
    def exitPassword_value(self, ctx:FirebirdParser.Password_valueContext):
        pass


    # Enter a parse tree produced by FirebirdParser#link_authentication.
    def enterLink_authentication(self, ctx:FirebirdParser.Link_authenticationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#link_authentication.
    def exitLink_authentication(self, ctx:FirebirdParser.Link_authenticationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_schema.
    def enterCreate_schema(self, ctx:FirebirdParser.Create_schemaContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_schema.
    def exitCreate_schema(self, ctx:FirebirdParser.Create_schemaContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_database.
    def enterCreate_database(self, ctx:FirebirdParser.Create_databaseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_database.
    def exitCreate_database(self, ctx:FirebirdParser.Create_databaseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#database_logging_clauses.
    def enterDatabase_logging_clauses(self, ctx:FirebirdParser.Database_logging_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#database_logging_clauses.
    def exitDatabase_logging_clauses(self, ctx:FirebirdParser.Database_logging_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#database_logging_sub_clause.
    def enterDatabase_logging_sub_clause(self, ctx:FirebirdParser.Database_logging_sub_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#database_logging_sub_clause.
    def exitDatabase_logging_sub_clause(self, ctx:FirebirdParser.Database_logging_sub_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#tablespace_clauses.
    def enterTablespace_clauses(self, ctx:FirebirdParser.Tablespace_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#tablespace_clauses.
    def exitTablespace_clauses(self, ctx:FirebirdParser.Tablespace_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#enable_pluggable_database.
    def enterEnable_pluggable_database(self, ctx:FirebirdParser.Enable_pluggable_databaseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#enable_pluggable_database.
    def exitEnable_pluggable_database(self, ctx:FirebirdParser.Enable_pluggable_databaseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#file_name_convert.
    def enterFile_name_convert(self, ctx:FirebirdParser.File_name_convertContext):
        pass

    # Exit a parse tree produced by FirebirdParser#file_name_convert.
    def exitFile_name_convert(self, ctx:FirebirdParser.File_name_convertContext):
        pass


    # Enter a parse tree produced by FirebirdParser#filename_convert_sub_clause.
    def enterFilename_convert_sub_clause(self, ctx:FirebirdParser.Filename_convert_sub_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#filename_convert_sub_clause.
    def exitFilename_convert_sub_clause(self, ctx:FirebirdParser.Filename_convert_sub_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#tablespace_datafile_clauses.
    def enterTablespace_datafile_clauses(self, ctx:FirebirdParser.Tablespace_datafile_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#tablespace_datafile_clauses.
    def exitTablespace_datafile_clauses(self, ctx:FirebirdParser.Tablespace_datafile_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#undo_mode_clause.
    def enterUndo_mode_clause(self, ctx:FirebirdParser.Undo_mode_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#undo_mode_clause.
    def exitUndo_mode_clause(self, ctx:FirebirdParser.Undo_mode_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#default_tablespace.
    def enterDefault_tablespace(self, ctx:FirebirdParser.Default_tablespaceContext):
        pass

    # Exit a parse tree produced by FirebirdParser#default_tablespace.
    def exitDefault_tablespace(self, ctx:FirebirdParser.Default_tablespaceContext):
        pass


    # Enter a parse tree produced by FirebirdParser#default_temp_tablespace.
    def enterDefault_temp_tablespace(self, ctx:FirebirdParser.Default_temp_tablespaceContext):
        pass

    # Exit a parse tree produced by FirebirdParser#default_temp_tablespace.
    def exitDefault_temp_tablespace(self, ctx:FirebirdParser.Default_temp_tablespaceContext):
        pass


    # Enter a parse tree produced by FirebirdParser#undo_tablespace.
    def enterUndo_tablespace(self, ctx:FirebirdParser.Undo_tablespaceContext):
        pass

    # Exit a parse tree produced by FirebirdParser#undo_tablespace.
    def exitUndo_tablespace(self, ctx:FirebirdParser.Undo_tablespaceContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_database.
    def enterDrop_database(self, ctx:FirebirdParser.Drop_databaseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_database.
    def exitDrop_database(self, ctx:FirebirdParser.Drop_databaseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#create_database_link.
    def enterCreate_database_link(self, ctx:FirebirdParser.Create_database_linkContext):
        pass

    # Exit a parse tree produced by FirebirdParser#create_database_link.
    def exitCreate_database_link(self, ctx:FirebirdParser.Create_database_linkContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_database_link.
    def enterDrop_database_link(self, ctx:FirebirdParser.Drop_database_linkContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_database_link.
    def exitDrop_database_link(self, ctx:FirebirdParser.Drop_database_linkContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_tablespace_set.
    def enterAlter_tablespace_set(self, ctx:FirebirdParser.Alter_tablespace_setContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_tablespace_set.
    def exitAlter_tablespace_set(self, ctx:FirebirdParser.Alter_tablespace_setContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_tablespace_attrs.
    def enterAlter_tablespace_attrs(self, ctx:FirebirdParser.Alter_tablespace_attrsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_tablespace_attrs.
    def exitAlter_tablespace_attrs(self, ctx:FirebirdParser.Alter_tablespace_attrsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_tablespace_encryption.
    def enterAlter_tablespace_encryption(self, ctx:FirebirdParser.Alter_tablespace_encryptionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_tablespace_encryption.
    def exitAlter_tablespace_encryption(self, ctx:FirebirdParser.Alter_tablespace_encryptionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#ts_file_name_convert.
    def enterTs_file_name_convert(self, ctx:FirebirdParser.Ts_file_name_convertContext):
        pass

    # Exit a parse tree produced by FirebirdParser#ts_file_name_convert.
    def exitTs_file_name_convert(self, ctx:FirebirdParser.Ts_file_name_convertContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_role.
    def enterAlter_role(self, ctx:FirebirdParser.Alter_roleContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_role.
    def exitAlter_role(self, ctx:FirebirdParser.Alter_roleContext):
        pass


    # Enter a parse tree produced by FirebirdParser#role_identified_clause.
    def enterRole_identified_clause(self, ctx:FirebirdParser.Role_identified_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#role_identified_clause.
    def exitRole_identified_clause(self, ctx:FirebirdParser.Role_identified_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_table.
    def enterAlter_table(self, ctx:FirebirdParser.Alter_tableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_table.
    def exitAlter_table(self, ctx:FirebirdParser.Alter_tableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#memoptimize_read_write_clause.
    def enterMemoptimize_read_write_clause(self, ctx:FirebirdParser.Memoptimize_read_write_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#memoptimize_read_write_clause.
    def exitMemoptimize_read_write_clause(self, ctx:FirebirdParser.Memoptimize_read_write_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_table_properties.
    def enterAlter_table_properties(self, ctx:FirebirdParser.Alter_table_propertiesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_table_properties.
    def exitAlter_table_properties(self, ctx:FirebirdParser.Alter_table_propertiesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_table_partitioning.
    def enterAlter_table_partitioning(self, ctx:FirebirdParser.Alter_table_partitioningContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_table_partitioning.
    def exitAlter_table_partitioning(self, ctx:FirebirdParser.Alter_table_partitioningContext):
        pass


    # Enter a parse tree produced by FirebirdParser#add_table_partition.
    def enterAdd_table_partition(self, ctx:FirebirdParser.Add_table_partitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#add_table_partition.
    def exitAdd_table_partition(self, ctx:FirebirdParser.Add_table_partitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_table_partition.
    def enterDrop_table_partition(self, ctx:FirebirdParser.Drop_table_partitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_table_partition.
    def exitDrop_table_partition(self, ctx:FirebirdParser.Drop_table_partitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#merge_table_partition.
    def enterMerge_table_partition(self, ctx:FirebirdParser.Merge_table_partitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#merge_table_partition.
    def exitMerge_table_partition(self, ctx:FirebirdParser.Merge_table_partitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#modify_table_partition.
    def enterModify_table_partition(self, ctx:FirebirdParser.Modify_table_partitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#modify_table_partition.
    def exitModify_table_partition(self, ctx:FirebirdParser.Modify_table_partitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#split_table_partition.
    def enterSplit_table_partition(self, ctx:FirebirdParser.Split_table_partitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#split_table_partition.
    def exitSplit_table_partition(self, ctx:FirebirdParser.Split_table_partitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#truncate_table_partition.
    def enterTruncate_table_partition(self, ctx:FirebirdParser.Truncate_table_partitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#truncate_table_partition.
    def exitTruncate_table_partition(self, ctx:FirebirdParser.Truncate_table_partitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#exchange_table_partition.
    def enterExchange_table_partition(self, ctx:FirebirdParser.Exchange_table_partitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#exchange_table_partition.
    def exitExchange_table_partition(self, ctx:FirebirdParser.Exchange_table_partitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#coalesce_table_partition.
    def enterCoalesce_table_partition(self, ctx:FirebirdParser.Coalesce_table_partitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#coalesce_table_partition.
    def exitCoalesce_table_partition(self, ctx:FirebirdParser.Coalesce_table_partitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_interval_partition.
    def enterAlter_interval_partition(self, ctx:FirebirdParser.Alter_interval_partitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_interval_partition.
    def exitAlter_interval_partition(self, ctx:FirebirdParser.Alter_interval_partitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#move_table_partition.
    def enterMove_table_partition(self, ctx:FirebirdParser.Move_table_partitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#move_table_partition.
    def exitMove_table_partition(self, ctx:FirebirdParser.Move_table_partitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#filter_condition.
    def enterFilter_condition(self, ctx:FirebirdParser.Filter_conditionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#filter_condition.
    def exitFilter_condition(self, ctx:FirebirdParser.Filter_conditionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#rename_table_partition.
    def enterRename_table_partition(self, ctx:FirebirdParser.Rename_table_partitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#rename_table_partition.
    def exitRename_table_partition(self, ctx:FirebirdParser.Rename_table_partitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#partition_extended_names.
    def enterPartition_extended_names(self, ctx:FirebirdParser.Partition_extended_namesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#partition_extended_names.
    def exitPartition_extended_names(self, ctx:FirebirdParser.Partition_extended_namesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#subpartition_extended_names.
    def enterSubpartition_extended_names(self, ctx:FirebirdParser.Subpartition_extended_namesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#subpartition_extended_names.
    def exitSubpartition_extended_names(self, ctx:FirebirdParser.Subpartition_extended_namesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_table_properties_1.
    def enterAlter_table_properties_1(self, ctx:FirebirdParser.Alter_table_properties_1Context):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_table_properties_1.
    def exitAlter_table_properties_1(self, ctx:FirebirdParser.Alter_table_properties_1Context):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_iot_clauses.
    def enterAlter_iot_clauses(self, ctx:FirebirdParser.Alter_iot_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_iot_clauses.
    def exitAlter_iot_clauses(self, ctx:FirebirdParser.Alter_iot_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_mapping_table_clause.
    def enterAlter_mapping_table_clause(self, ctx:FirebirdParser.Alter_mapping_table_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_mapping_table_clause.
    def exitAlter_mapping_table_clause(self, ctx:FirebirdParser.Alter_mapping_table_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#alter_overflow_clause.
    def enterAlter_overflow_clause(self, ctx:FirebirdParser.Alter_overflow_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#alter_overflow_clause.
    def exitAlter_overflow_clause(self, ctx:FirebirdParser.Alter_overflow_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#add_overflow_clause.
    def enterAdd_overflow_clause(self, ctx:FirebirdParser.Add_overflow_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#add_overflow_clause.
    def exitAdd_overflow_clause(self, ctx:FirebirdParser.Add_overflow_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#update_index_clauses.
    def enterUpdate_index_clauses(self, ctx:FirebirdParser.Update_index_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#update_index_clauses.
    def exitUpdate_index_clauses(self, ctx:FirebirdParser.Update_index_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#update_global_index_clause.
    def enterUpdate_global_index_clause(self, ctx:FirebirdParser.Update_global_index_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#update_global_index_clause.
    def exitUpdate_global_index_clause(self, ctx:FirebirdParser.Update_global_index_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#update_all_indexes_clause.
    def enterUpdate_all_indexes_clause(self, ctx:FirebirdParser.Update_all_indexes_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#update_all_indexes_clause.
    def exitUpdate_all_indexes_clause(self, ctx:FirebirdParser.Update_all_indexes_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#update_all_indexes_index_clause.
    def enterUpdate_all_indexes_index_clause(self, ctx:FirebirdParser.Update_all_indexes_index_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#update_all_indexes_index_clause.
    def exitUpdate_all_indexes_index_clause(self, ctx:FirebirdParser.Update_all_indexes_index_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#update_index_partition.
    def enterUpdate_index_partition(self, ctx:FirebirdParser.Update_index_partitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#update_index_partition.
    def exitUpdate_index_partition(self, ctx:FirebirdParser.Update_index_partitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#update_index_subpartition.
    def enterUpdate_index_subpartition(self, ctx:FirebirdParser.Update_index_subpartitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#update_index_subpartition.
    def exitUpdate_index_subpartition(self, ctx:FirebirdParser.Update_index_subpartitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#enable_disable_clause.
    def enterEnable_disable_clause(self, ctx:FirebirdParser.Enable_disable_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#enable_disable_clause.
    def exitEnable_disable_clause(self, ctx:FirebirdParser.Enable_disable_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#using_index_clause.
    def enterUsing_index_clause(self, ctx:FirebirdParser.Using_index_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#using_index_clause.
    def exitUsing_index_clause(self, ctx:FirebirdParser.Using_index_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#index_attributes.
    def enterIndex_attributes(self, ctx:FirebirdParser.Index_attributesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#index_attributes.
    def exitIndex_attributes(self, ctx:FirebirdParser.Index_attributesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#sort_or_nosort.
    def enterSort_or_nosort(self, ctx:FirebirdParser.Sort_or_nosortContext):
        pass

    # Exit a parse tree produced by FirebirdParser#sort_or_nosort.
    def exitSort_or_nosort(self, ctx:FirebirdParser.Sort_or_nosortContext):
        pass


    # Enter a parse tree produced by FirebirdParser#exceptions_clause.
    def enterExceptions_clause(self, ctx:FirebirdParser.Exceptions_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#exceptions_clause.
    def exitExceptions_clause(self, ctx:FirebirdParser.Exceptions_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#move_table_clause.
    def enterMove_table_clause(self, ctx:FirebirdParser.Move_table_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#move_table_clause.
    def exitMove_table_clause(self, ctx:FirebirdParser.Move_table_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#index_org_table_clause.
    def enterIndex_org_table_clause(self, ctx:FirebirdParser.Index_org_table_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#index_org_table_clause.
    def exitIndex_org_table_clause(self, ctx:FirebirdParser.Index_org_table_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#mapping_table_clause.
    def enterMapping_table_clause(self, ctx:FirebirdParser.Mapping_table_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#mapping_table_clause.
    def exitMapping_table_clause(self, ctx:FirebirdParser.Mapping_table_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#key_compression.
    def enterKey_compression(self, ctx:FirebirdParser.Key_compressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#key_compression.
    def exitKey_compression(self, ctx:FirebirdParser.Key_compressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#index_org_overflow_clause.
    def enterIndex_org_overflow_clause(self, ctx:FirebirdParser.Index_org_overflow_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#index_org_overflow_clause.
    def exitIndex_org_overflow_clause(self, ctx:FirebirdParser.Index_org_overflow_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#column_clauses.
    def enterColumn_clauses(self, ctx:FirebirdParser.Column_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#column_clauses.
    def exitColumn_clauses(self, ctx:FirebirdParser.Column_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#modify_collection_retrieval.
    def enterModify_collection_retrieval(self, ctx:FirebirdParser.Modify_collection_retrievalContext):
        pass

    # Exit a parse tree produced by FirebirdParser#modify_collection_retrieval.
    def exitModify_collection_retrieval(self, ctx:FirebirdParser.Modify_collection_retrievalContext):
        pass


    # Enter a parse tree produced by FirebirdParser#collection_item.
    def enterCollection_item(self, ctx:FirebirdParser.Collection_itemContext):
        pass

    # Exit a parse tree produced by FirebirdParser#collection_item.
    def exitCollection_item(self, ctx:FirebirdParser.Collection_itemContext):
        pass


    # Enter a parse tree produced by FirebirdParser#rename_column_clause.
    def enterRename_column_clause(self, ctx:FirebirdParser.Rename_column_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#rename_column_clause.
    def exitRename_column_clause(self, ctx:FirebirdParser.Rename_column_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#old_column_name.
    def enterOld_column_name(self, ctx:FirebirdParser.Old_column_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#old_column_name.
    def exitOld_column_name(self, ctx:FirebirdParser.Old_column_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#new_column_name.
    def enterNew_column_name(self, ctx:FirebirdParser.New_column_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#new_column_name.
    def exitNew_column_name(self, ctx:FirebirdParser.New_column_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#add_modify_drop_column_clauses.
    def enterAdd_modify_drop_column_clauses(self, ctx:FirebirdParser.Add_modify_drop_column_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#add_modify_drop_column_clauses.
    def exitAdd_modify_drop_column_clauses(self, ctx:FirebirdParser.Add_modify_drop_column_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_column_clause.
    def enterDrop_column_clause(self, ctx:FirebirdParser.Drop_column_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_column_clause.
    def exitDrop_column_clause(self, ctx:FirebirdParser.Drop_column_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#modify_column_clauses.
    def enterModify_column_clauses(self, ctx:FirebirdParser.Modify_column_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#modify_column_clauses.
    def exitModify_column_clauses(self, ctx:FirebirdParser.Modify_column_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#modify_col_properties.
    def enterModify_col_properties(self, ctx:FirebirdParser.Modify_col_propertiesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#modify_col_properties.
    def exitModify_col_properties(self, ctx:FirebirdParser.Modify_col_propertiesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#modify_col_visibility.
    def enterModify_col_visibility(self, ctx:FirebirdParser.Modify_col_visibilityContext):
        pass

    # Exit a parse tree produced by FirebirdParser#modify_col_visibility.
    def exitModify_col_visibility(self, ctx:FirebirdParser.Modify_col_visibilityContext):
        pass


    # Enter a parse tree produced by FirebirdParser#modify_col_substitutable.
    def enterModify_col_substitutable(self, ctx:FirebirdParser.Modify_col_substitutableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#modify_col_substitutable.
    def exitModify_col_substitutable(self, ctx:FirebirdParser.Modify_col_substitutableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#add_column_clause.
    def enterAdd_column_clause(self, ctx:FirebirdParser.Add_column_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#add_column_clause.
    def exitAdd_column_clause(self, ctx:FirebirdParser.Add_column_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#varray_col_properties.
    def enterVarray_col_properties(self, ctx:FirebirdParser.Varray_col_propertiesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#varray_col_properties.
    def exitVarray_col_properties(self, ctx:FirebirdParser.Varray_col_propertiesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#varray_storage_clause.
    def enterVarray_storage_clause(self, ctx:FirebirdParser.Varray_storage_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#varray_storage_clause.
    def exitVarray_storage_clause(self, ctx:FirebirdParser.Varray_storage_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lob_segname.
    def enterLob_segname(self, ctx:FirebirdParser.Lob_segnameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lob_segname.
    def exitLob_segname(self, ctx:FirebirdParser.Lob_segnameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lob_item.
    def enterLob_item(self, ctx:FirebirdParser.Lob_itemContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lob_item.
    def exitLob_item(self, ctx:FirebirdParser.Lob_itemContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lob_storage_parameters.
    def enterLob_storage_parameters(self, ctx:FirebirdParser.Lob_storage_parametersContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lob_storage_parameters.
    def exitLob_storage_parameters(self, ctx:FirebirdParser.Lob_storage_parametersContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lob_storage_clause.
    def enterLob_storage_clause(self, ctx:FirebirdParser.Lob_storage_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lob_storage_clause.
    def exitLob_storage_clause(self, ctx:FirebirdParser.Lob_storage_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#modify_lob_storage_clause.
    def enterModify_lob_storage_clause(self, ctx:FirebirdParser.Modify_lob_storage_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#modify_lob_storage_clause.
    def exitModify_lob_storage_clause(self, ctx:FirebirdParser.Modify_lob_storage_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#modify_lob_parameters.
    def enterModify_lob_parameters(self, ctx:FirebirdParser.Modify_lob_parametersContext):
        pass

    # Exit a parse tree produced by FirebirdParser#modify_lob_parameters.
    def exitModify_lob_parameters(self, ctx:FirebirdParser.Modify_lob_parametersContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lob_parameters.
    def enterLob_parameters(self, ctx:FirebirdParser.Lob_parametersContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lob_parameters.
    def exitLob_parameters(self, ctx:FirebirdParser.Lob_parametersContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lob_deduplicate_clause.
    def enterLob_deduplicate_clause(self, ctx:FirebirdParser.Lob_deduplicate_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lob_deduplicate_clause.
    def exitLob_deduplicate_clause(self, ctx:FirebirdParser.Lob_deduplicate_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lob_compression_clause.
    def enterLob_compression_clause(self, ctx:FirebirdParser.Lob_compression_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lob_compression_clause.
    def exitLob_compression_clause(self, ctx:FirebirdParser.Lob_compression_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lob_retention_clause.
    def enterLob_retention_clause(self, ctx:FirebirdParser.Lob_retention_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lob_retention_clause.
    def exitLob_retention_clause(self, ctx:FirebirdParser.Lob_retention_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#encryption_spec.
    def enterEncryption_spec(self, ctx:FirebirdParser.Encryption_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#encryption_spec.
    def exitEncryption_spec(self, ctx:FirebirdParser.Encryption_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#tablespace.
    def enterTablespace(self, ctx:FirebirdParser.TablespaceContext):
        pass

    # Exit a parse tree produced by FirebirdParser#tablespace.
    def exitTablespace(self, ctx:FirebirdParser.TablespaceContext):
        pass


    # Enter a parse tree produced by FirebirdParser#varray_item.
    def enterVarray_item(self, ctx:FirebirdParser.Varray_itemContext):
        pass

    # Exit a parse tree produced by FirebirdParser#varray_item.
    def exitVarray_item(self, ctx:FirebirdParser.Varray_itemContext):
        pass


    # Enter a parse tree produced by FirebirdParser#column_properties.
    def enterColumn_properties(self, ctx:FirebirdParser.Column_propertiesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#column_properties.
    def exitColumn_properties(self, ctx:FirebirdParser.Column_propertiesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lob_partition_storage.
    def enterLob_partition_storage(self, ctx:FirebirdParser.Lob_partition_storageContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lob_partition_storage.
    def exitLob_partition_storage(self, ctx:FirebirdParser.Lob_partition_storageContext):
        pass


    # Enter a parse tree produced by FirebirdParser#period_definition.
    def enterPeriod_definition(self, ctx:FirebirdParser.Period_definitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#period_definition.
    def exitPeriod_definition(self, ctx:FirebirdParser.Period_definitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#start_time_column.
    def enterStart_time_column(self, ctx:FirebirdParser.Start_time_columnContext):
        pass

    # Exit a parse tree produced by FirebirdParser#start_time_column.
    def exitStart_time_column(self, ctx:FirebirdParser.Start_time_columnContext):
        pass


    # Enter a parse tree produced by FirebirdParser#end_time_column.
    def enterEnd_time_column(self, ctx:FirebirdParser.End_time_columnContext):
        pass

    # Exit a parse tree produced by FirebirdParser#end_time_column.
    def exitEnd_time_column(self, ctx:FirebirdParser.End_time_columnContext):
        pass


    # Enter a parse tree produced by FirebirdParser#column_definition.
    def enterColumn_definition(self, ctx:FirebirdParser.Column_definitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#column_definition.
    def exitColumn_definition(self, ctx:FirebirdParser.Column_definitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#column_collation_name.
    def enterColumn_collation_name(self, ctx:FirebirdParser.Column_collation_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#column_collation_name.
    def exitColumn_collation_name(self, ctx:FirebirdParser.Column_collation_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#identity_clause.
    def enterIdentity_clause(self, ctx:FirebirdParser.Identity_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#identity_clause.
    def exitIdentity_clause(self, ctx:FirebirdParser.Identity_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#identity_options_parentheses.
    def enterIdentity_options_parentheses(self, ctx:FirebirdParser.Identity_options_parenthesesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#identity_options_parentheses.
    def exitIdentity_options_parentheses(self, ctx:FirebirdParser.Identity_options_parenthesesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#identity_options.
    def enterIdentity_options(self, ctx:FirebirdParser.Identity_optionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#identity_options.
    def exitIdentity_options(self, ctx:FirebirdParser.Identity_optionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#virtual_column_definition.
    def enterVirtual_column_definition(self, ctx:FirebirdParser.Virtual_column_definitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#virtual_column_definition.
    def exitVirtual_column_definition(self, ctx:FirebirdParser.Virtual_column_definitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#virtual_column_expression.
    def enterVirtual_column_expression(self, ctx:FirebirdParser.Virtual_column_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#virtual_column_expression.
    def exitVirtual_column_expression(self, ctx:FirebirdParser.Virtual_column_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#autogenerated_sequence_definition.
    def enterAutogenerated_sequence_definition(self, ctx:FirebirdParser.Autogenerated_sequence_definitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#autogenerated_sequence_definition.
    def exitAutogenerated_sequence_definition(self, ctx:FirebirdParser.Autogenerated_sequence_definitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#by_user_for_statistics_clause.
    def enterBy_user_for_statistics_clause(self, ctx:FirebirdParser.By_user_for_statistics_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#by_user_for_statistics_clause.
    def exitBy_user_for_statistics_clause(self, ctx:FirebirdParser.By_user_for_statistics_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#evaluation_edition_clause.
    def enterEvaluation_edition_clause(self, ctx:FirebirdParser.Evaluation_edition_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#evaluation_edition_clause.
    def exitEvaluation_edition_clause(self, ctx:FirebirdParser.Evaluation_edition_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#nested_table_col_properties.
    def enterNested_table_col_properties(self, ctx:FirebirdParser.Nested_table_col_propertiesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#nested_table_col_properties.
    def exitNested_table_col_properties(self, ctx:FirebirdParser.Nested_table_col_propertiesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#nested_item.
    def enterNested_item(self, ctx:FirebirdParser.Nested_itemContext):
        pass

    # Exit a parse tree produced by FirebirdParser#nested_item.
    def exitNested_item(self, ctx:FirebirdParser.Nested_itemContext):
        pass


    # Enter a parse tree produced by FirebirdParser#substitutable_column_clause.
    def enterSubstitutable_column_clause(self, ctx:FirebirdParser.Substitutable_column_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#substitutable_column_clause.
    def exitSubstitutable_column_clause(self, ctx:FirebirdParser.Substitutable_column_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#partition_name.
    def enterPartition_name(self, ctx:FirebirdParser.Partition_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#partition_name.
    def exitPartition_name(self, ctx:FirebirdParser.Partition_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#supplemental_logging_props.
    def enterSupplemental_logging_props(self, ctx:FirebirdParser.Supplemental_logging_propsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#supplemental_logging_props.
    def exitSupplemental_logging_props(self, ctx:FirebirdParser.Supplemental_logging_propsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#object_type_col_properties.
    def enterObject_type_col_properties(self, ctx:FirebirdParser.Object_type_col_propertiesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#object_type_col_properties.
    def exitObject_type_col_properties(self, ctx:FirebirdParser.Object_type_col_propertiesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#constraint_clauses.
    def enterConstraint_clauses(self, ctx:FirebirdParser.Constraint_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#constraint_clauses.
    def exitConstraint_clauses(self, ctx:FirebirdParser.Constraint_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#old_constraint_name.
    def enterOld_constraint_name(self, ctx:FirebirdParser.Old_constraint_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#old_constraint_name.
    def exitOld_constraint_name(self, ctx:FirebirdParser.Old_constraint_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#new_constraint_name.
    def enterNew_constraint_name(self, ctx:FirebirdParser.New_constraint_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#new_constraint_name.
    def exitNew_constraint_name(self, ctx:FirebirdParser.New_constraint_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#drop_constraint_clause.
    def enterDrop_constraint_clause(self, ctx:FirebirdParser.Drop_constraint_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#drop_constraint_clause.
    def exitDrop_constraint_clause(self, ctx:FirebirdParser.Drop_constraint_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#check_constraint.
    def enterCheck_constraint(self, ctx:FirebirdParser.Check_constraintContext):
        pass

    # Exit a parse tree produced by FirebirdParser#check_constraint.
    def exitCheck_constraint(self, ctx:FirebirdParser.Check_constraintContext):
        pass


    # Enter a parse tree produced by FirebirdParser#foreign_key_clause.
    def enterForeign_key_clause(self, ctx:FirebirdParser.Foreign_key_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#foreign_key_clause.
    def exitForeign_key_clause(self, ctx:FirebirdParser.Foreign_key_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#references_clause.
    def enterReferences_clause(self, ctx:FirebirdParser.References_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#references_clause.
    def exitReferences_clause(self, ctx:FirebirdParser.References_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#on_delete_clause.
    def enterOn_delete_clause(self, ctx:FirebirdParser.On_delete_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#on_delete_clause.
    def exitOn_delete_clause(self, ctx:FirebirdParser.On_delete_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#anonymous_block.
    def enterAnonymous_block(self, ctx:FirebirdParser.Anonymous_blockContext):
        pass

    # Exit a parse tree produced by FirebirdParser#anonymous_block.
    def exitAnonymous_block(self, ctx:FirebirdParser.Anonymous_blockContext):
        pass


    # Enter a parse tree produced by FirebirdParser#invoker_rights_clause.
    def enterInvoker_rights_clause(self, ctx:FirebirdParser.Invoker_rights_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#invoker_rights_clause.
    def exitInvoker_rights_clause(self, ctx:FirebirdParser.Invoker_rights_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#call_spec.
    def enterCall_spec(self, ctx:FirebirdParser.Call_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#call_spec.
    def exitCall_spec(self, ctx:FirebirdParser.Call_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#java_spec.
    def enterJava_spec(self, ctx:FirebirdParser.Java_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#java_spec.
    def exitJava_spec(self, ctx:FirebirdParser.Java_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#c_spec.
    def enterC_spec(self, ctx:FirebirdParser.C_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#c_spec.
    def exitC_spec(self, ctx:FirebirdParser.C_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#c_agent_in_clause.
    def enterC_agent_in_clause(self, ctx:FirebirdParser.C_agent_in_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#c_agent_in_clause.
    def exitC_agent_in_clause(self, ctx:FirebirdParser.C_agent_in_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#c_parameters_clause.
    def enterC_parameters_clause(self, ctx:FirebirdParser.C_parameters_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#c_parameters_clause.
    def exitC_parameters_clause(self, ctx:FirebirdParser.C_parameters_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#c_external_parameter.
    def enterC_external_parameter(self, ctx:FirebirdParser.C_external_parameterContext):
        pass

    # Exit a parse tree produced by FirebirdParser#c_external_parameter.
    def exitC_external_parameter(self, ctx:FirebirdParser.C_external_parameterContext):
        pass


    # Enter a parse tree produced by FirebirdParser#c_property.
    def enterC_property(self, ctx:FirebirdParser.C_propertyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#c_property.
    def exitC_property(self, ctx:FirebirdParser.C_propertyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#parameter.
    def enterParameter(self, ctx:FirebirdParser.ParameterContext):
        pass

    # Exit a parse tree produced by FirebirdParser#parameter.
    def exitParameter(self, ctx:FirebirdParser.ParameterContext):
        pass


    # Enter a parse tree produced by FirebirdParser#default_value_part.
    def enterDefault_value_part(self, ctx:FirebirdParser.Default_value_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#default_value_part.
    def exitDefault_value_part(self, ctx:FirebirdParser.Default_value_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#seq_of_declare_specs.
    def enterSeq_of_declare_specs(self, ctx:FirebirdParser.Seq_of_declare_specsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#seq_of_declare_specs.
    def exitSeq_of_declare_specs(self, ctx:FirebirdParser.Seq_of_declare_specsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#declare_spec.
    def enterDeclare_spec(self, ctx:FirebirdParser.Declare_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#declare_spec.
    def exitDeclare_spec(self, ctx:FirebirdParser.Declare_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#variable_declaration.
    def enterVariable_declaration(self, ctx:FirebirdParser.Variable_declarationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#variable_declaration.
    def exitVariable_declaration(self, ctx:FirebirdParser.Variable_declarationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#subtype_declaration.
    def enterSubtype_declaration(self, ctx:FirebirdParser.Subtype_declarationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#subtype_declaration.
    def exitSubtype_declaration(self, ctx:FirebirdParser.Subtype_declarationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#cursor_declaration.
    def enterCursor_declaration(self, ctx:FirebirdParser.Cursor_declarationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#cursor_declaration.
    def exitCursor_declaration(self, ctx:FirebirdParser.Cursor_declarationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#parameter_spec.
    def enterParameter_spec(self, ctx:FirebirdParser.Parameter_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#parameter_spec.
    def exitParameter_spec(self, ctx:FirebirdParser.Parameter_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#exception_declaration.
    def enterException_declaration(self, ctx:FirebirdParser.Exception_declarationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#exception_declaration.
    def exitException_declaration(self, ctx:FirebirdParser.Exception_declarationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#pragma_declaration.
    def enterPragma_declaration(self, ctx:FirebirdParser.Pragma_declarationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#pragma_declaration.
    def exitPragma_declaration(self, ctx:FirebirdParser.Pragma_declarationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#record_type_def.
    def enterRecord_type_def(self, ctx:FirebirdParser.Record_type_defContext):
        pass

    # Exit a parse tree produced by FirebirdParser#record_type_def.
    def exitRecord_type_def(self, ctx:FirebirdParser.Record_type_defContext):
        pass


    # Enter a parse tree produced by FirebirdParser#field_spec.
    def enterField_spec(self, ctx:FirebirdParser.Field_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#field_spec.
    def exitField_spec(self, ctx:FirebirdParser.Field_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#ref_cursor_type_def.
    def enterRef_cursor_type_def(self, ctx:FirebirdParser.Ref_cursor_type_defContext):
        pass

    # Exit a parse tree produced by FirebirdParser#ref_cursor_type_def.
    def exitRef_cursor_type_def(self, ctx:FirebirdParser.Ref_cursor_type_defContext):
        pass


    # Enter a parse tree produced by FirebirdParser#type_declaration.
    def enterType_declaration(self, ctx:FirebirdParser.Type_declarationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#type_declaration.
    def exitType_declaration(self, ctx:FirebirdParser.Type_declarationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#table_type_def.
    def enterTable_type_def(self, ctx:FirebirdParser.Table_type_defContext):
        pass

    # Exit a parse tree produced by FirebirdParser#table_type_def.
    def exitTable_type_def(self, ctx:FirebirdParser.Table_type_defContext):
        pass


    # Enter a parse tree produced by FirebirdParser#table_indexed_by_part.
    def enterTable_indexed_by_part(self, ctx:FirebirdParser.Table_indexed_by_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#table_indexed_by_part.
    def exitTable_indexed_by_part(self, ctx:FirebirdParser.Table_indexed_by_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#varray_type_def.
    def enterVarray_type_def(self, ctx:FirebirdParser.Varray_type_defContext):
        pass

    # Exit a parse tree produced by FirebirdParser#varray_type_def.
    def exitVarray_type_def(self, ctx:FirebirdParser.Varray_type_defContext):
        pass


    # Enter a parse tree produced by FirebirdParser#seq_of_statements.
    def enterSeq_of_statements(self, ctx:FirebirdParser.Seq_of_statementsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#seq_of_statements.
    def exitSeq_of_statements(self, ctx:FirebirdParser.Seq_of_statementsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#label_declaration.
    def enterLabel_declaration(self, ctx:FirebirdParser.Label_declarationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#label_declaration.
    def exitLabel_declaration(self, ctx:FirebirdParser.Label_declarationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#statement.
    def enterStatement(self, ctx:FirebirdParser.StatementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#statement.
    def exitStatement(self, ctx:FirebirdParser.StatementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#assignment_statement.
    def enterAssignment_statement(self, ctx:FirebirdParser.Assignment_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#assignment_statement.
    def exitAssignment_statement(self, ctx:FirebirdParser.Assignment_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#continue_statement.
    def enterContinue_statement(self, ctx:FirebirdParser.Continue_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#continue_statement.
    def exitContinue_statement(self, ctx:FirebirdParser.Continue_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#exit_statement.
    def enterExit_statement(self, ctx:FirebirdParser.Exit_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#exit_statement.
    def exitExit_statement(self, ctx:FirebirdParser.Exit_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#goto_statement.
    def enterGoto_statement(self, ctx:FirebirdParser.Goto_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#goto_statement.
    def exitGoto_statement(self, ctx:FirebirdParser.Goto_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#if_statement.
    def enterIf_statement(self, ctx:FirebirdParser.If_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#if_statement.
    def exitIf_statement(self, ctx:FirebirdParser.If_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#elsif_part.
    def enterElsif_part(self, ctx:FirebirdParser.Elsif_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#elsif_part.
    def exitElsif_part(self, ctx:FirebirdParser.Elsif_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#else_part.
    def enterElse_part(self, ctx:FirebirdParser.Else_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#else_part.
    def exitElse_part(self, ctx:FirebirdParser.Else_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#loop_statement.
    def enterLoop_statement(self, ctx:FirebirdParser.Loop_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#loop_statement.
    def exitLoop_statement(self, ctx:FirebirdParser.Loop_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#cursor_loop_param.
    def enterCursor_loop_param(self, ctx:FirebirdParser.Cursor_loop_paramContext):
        pass

    # Exit a parse tree produced by FirebirdParser#cursor_loop_param.
    def exitCursor_loop_param(self, ctx:FirebirdParser.Cursor_loop_paramContext):
        pass


    # Enter a parse tree produced by FirebirdParser#forall_statement.
    def enterForall_statement(self, ctx:FirebirdParser.Forall_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#forall_statement.
    def exitForall_statement(self, ctx:FirebirdParser.Forall_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#bounds_clause.
    def enterBounds_clause(self, ctx:FirebirdParser.Bounds_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#bounds_clause.
    def exitBounds_clause(self, ctx:FirebirdParser.Bounds_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#between_bound.
    def enterBetween_bound(self, ctx:FirebirdParser.Between_boundContext):
        pass

    # Exit a parse tree produced by FirebirdParser#between_bound.
    def exitBetween_bound(self, ctx:FirebirdParser.Between_boundContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lower_bound.
    def enterLower_bound(self, ctx:FirebirdParser.Lower_boundContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lower_bound.
    def exitLower_bound(self, ctx:FirebirdParser.Lower_boundContext):
        pass


    # Enter a parse tree produced by FirebirdParser#upper_bound.
    def enterUpper_bound(self, ctx:FirebirdParser.Upper_boundContext):
        pass

    # Exit a parse tree produced by FirebirdParser#upper_bound.
    def exitUpper_bound(self, ctx:FirebirdParser.Upper_boundContext):
        pass


    # Enter a parse tree produced by FirebirdParser#null_statement.
    def enterNull_statement(self, ctx:FirebirdParser.Null_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#null_statement.
    def exitNull_statement(self, ctx:FirebirdParser.Null_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#raise_statement.
    def enterRaise_statement(self, ctx:FirebirdParser.Raise_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#raise_statement.
    def exitRaise_statement(self, ctx:FirebirdParser.Raise_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#return_statement.
    def enterReturn_statement(self, ctx:FirebirdParser.Return_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#return_statement.
    def exitReturn_statement(self, ctx:FirebirdParser.Return_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#call_statement.
    def enterCall_statement(self, ctx:FirebirdParser.Call_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#call_statement.
    def exitCall_statement(self, ctx:FirebirdParser.Call_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#pipe_row_statement.
    def enterPipe_row_statement(self, ctx:FirebirdParser.Pipe_row_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#pipe_row_statement.
    def exitPipe_row_statement(self, ctx:FirebirdParser.Pipe_row_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#selection_directive.
    def enterSelection_directive(self, ctx:FirebirdParser.Selection_directiveContext):
        pass

    # Exit a parse tree produced by FirebirdParser#selection_directive.
    def exitSelection_directive(self, ctx:FirebirdParser.Selection_directiveContext):
        pass


    # Enter a parse tree produced by FirebirdParser#error_directive.
    def enterError_directive(self, ctx:FirebirdParser.Error_directiveContext):
        pass

    # Exit a parse tree produced by FirebirdParser#error_directive.
    def exitError_directive(self, ctx:FirebirdParser.Error_directiveContext):
        pass


    # Enter a parse tree produced by FirebirdParser#selection_directive_body.
    def enterSelection_directive_body(self, ctx:FirebirdParser.Selection_directive_bodyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#selection_directive_body.
    def exitSelection_directive_body(self, ctx:FirebirdParser.Selection_directive_bodyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#body.
    def enterBody(self, ctx:FirebirdParser.BodyContext):
        pass

    # Exit a parse tree produced by FirebirdParser#body.
    def exitBody(self, ctx:FirebirdParser.BodyContext):
        pass


    # Enter a parse tree produced by FirebirdParser#exception_handler.
    def enterException_handler(self, ctx:FirebirdParser.Exception_handlerContext):
        pass

    # Exit a parse tree produced by FirebirdParser#exception_handler.
    def exitException_handler(self, ctx:FirebirdParser.Exception_handlerContext):
        pass


    # Enter a parse tree produced by FirebirdParser#trigger_block.
    def enterTrigger_block(self, ctx:FirebirdParser.Trigger_blockContext):
        pass

    # Exit a parse tree produced by FirebirdParser#trigger_block.
    def exitTrigger_block(self, ctx:FirebirdParser.Trigger_blockContext):
        pass


    # Enter a parse tree produced by FirebirdParser#tps_block.
    def enterTps_block(self, ctx:FirebirdParser.Tps_blockContext):
        pass

    # Exit a parse tree produced by FirebirdParser#tps_block.
    def exitTps_block(self, ctx:FirebirdParser.Tps_blockContext):
        pass


    # Enter a parse tree produced by FirebirdParser#block.
    def enterBlock(self, ctx:FirebirdParser.BlockContext):
        pass

    # Exit a parse tree produced by FirebirdParser#block.
    def exitBlock(self, ctx:FirebirdParser.BlockContext):
        pass


    # Enter a parse tree produced by FirebirdParser#sql_statement.
    def enterSql_statement(self, ctx:FirebirdParser.Sql_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#sql_statement.
    def exitSql_statement(self, ctx:FirebirdParser.Sql_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#execute_statement.
    def enterExecute_statement(self, ctx:FirebirdParser.Execute_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#execute_statement.
    def exitExecute_statement(self, ctx:FirebirdParser.Execute_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#dynamic_returning_clause.
    def enterDynamic_returning_clause(self, ctx:FirebirdParser.Dynamic_returning_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#dynamic_returning_clause.
    def exitDynamic_returning_clause(self, ctx:FirebirdParser.Dynamic_returning_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#data_manipulation_language_statements.
    def enterData_manipulation_language_statements(self, ctx:FirebirdParser.Data_manipulation_language_statementsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#data_manipulation_language_statements.
    def exitData_manipulation_language_statements(self, ctx:FirebirdParser.Data_manipulation_language_statementsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#cursor_manipulation_statements.
    def enterCursor_manipulation_statements(self, ctx:FirebirdParser.Cursor_manipulation_statementsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#cursor_manipulation_statements.
    def exitCursor_manipulation_statements(self, ctx:FirebirdParser.Cursor_manipulation_statementsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#close_statement.
    def enterClose_statement(self, ctx:FirebirdParser.Close_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#close_statement.
    def exitClose_statement(self, ctx:FirebirdParser.Close_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#open_statement.
    def enterOpen_statement(self, ctx:FirebirdParser.Open_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#open_statement.
    def exitOpen_statement(self, ctx:FirebirdParser.Open_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#fetch_statement.
    def enterFetch_statement(self, ctx:FirebirdParser.Fetch_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#fetch_statement.
    def exitFetch_statement(self, ctx:FirebirdParser.Fetch_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#variable_or_collection.
    def enterVariable_or_collection(self, ctx:FirebirdParser.Variable_or_collectionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#variable_or_collection.
    def exitVariable_or_collection(self, ctx:FirebirdParser.Variable_or_collectionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#open_for_statement.
    def enterOpen_for_statement(self, ctx:FirebirdParser.Open_for_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#open_for_statement.
    def exitOpen_for_statement(self, ctx:FirebirdParser.Open_for_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#transaction_control_statements.
    def enterTransaction_control_statements(self, ctx:FirebirdParser.Transaction_control_statementsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#transaction_control_statements.
    def exitTransaction_control_statements(self, ctx:FirebirdParser.Transaction_control_statementsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#set_transaction_command.
    def enterSet_transaction_command(self, ctx:FirebirdParser.Set_transaction_commandContext):
        pass

    # Exit a parse tree produced by FirebirdParser#set_transaction_command.
    def exitSet_transaction_command(self, ctx:FirebirdParser.Set_transaction_commandContext):
        pass


    # Enter a parse tree produced by FirebirdParser#set_constraint_command.
    def enterSet_constraint_command(self, ctx:FirebirdParser.Set_constraint_commandContext):
        pass

    # Exit a parse tree produced by FirebirdParser#set_constraint_command.
    def exitSet_constraint_command(self, ctx:FirebirdParser.Set_constraint_commandContext):
        pass


    # Enter a parse tree produced by FirebirdParser#commit_statement.
    def enterCommit_statement(self, ctx:FirebirdParser.Commit_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#commit_statement.
    def exitCommit_statement(self, ctx:FirebirdParser.Commit_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#write_clause.
    def enterWrite_clause(self, ctx:FirebirdParser.Write_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#write_clause.
    def exitWrite_clause(self, ctx:FirebirdParser.Write_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#rollback_statement.
    def enterRollback_statement(self, ctx:FirebirdParser.Rollback_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#rollback_statement.
    def exitRollback_statement(self, ctx:FirebirdParser.Rollback_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#savepoint_statement.
    def enterSavepoint_statement(self, ctx:FirebirdParser.Savepoint_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#savepoint_statement.
    def exitSavepoint_statement(self, ctx:FirebirdParser.Savepoint_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#collection_method_call.
    def enterCollection_method_call(self, ctx:FirebirdParser.Collection_method_callContext):
        pass

    # Exit a parse tree produced by FirebirdParser#collection_method_call.
    def exitCollection_method_call(self, ctx:FirebirdParser.Collection_method_callContext):
        pass


    # Enter a parse tree produced by FirebirdParser#explain_statement.
    def enterExplain_statement(self, ctx:FirebirdParser.Explain_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#explain_statement.
    def exitExplain_statement(self, ctx:FirebirdParser.Explain_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#select_only_statement.
    def enterSelect_only_statement(self, ctx:FirebirdParser.Select_only_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#select_only_statement.
    def exitSelect_only_statement(self, ctx:FirebirdParser.Select_only_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#select_statement.
    def enterSelect_statement(self, ctx:FirebirdParser.Select_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#select_statement.
    def exitSelect_statement(self, ctx:FirebirdParser.Select_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#with_clause.
    def enterWith_clause(self, ctx:FirebirdParser.With_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#with_clause.
    def exitWith_clause(self, ctx:FirebirdParser.With_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#with_factoring_clause.
    def enterWith_factoring_clause(self, ctx:FirebirdParser.With_factoring_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#with_factoring_clause.
    def exitWith_factoring_clause(self, ctx:FirebirdParser.With_factoring_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#subquery_factoring_clause.
    def enterSubquery_factoring_clause(self, ctx:FirebirdParser.Subquery_factoring_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#subquery_factoring_clause.
    def exitSubquery_factoring_clause(self, ctx:FirebirdParser.Subquery_factoring_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#search_clause.
    def enterSearch_clause(self, ctx:FirebirdParser.Search_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#search_clause.
    def exitSearch_clause(self, ctx:FirebirdParser.Search_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#cycle_clause.
    def enterCycle_clause(self, ctx:FirebirdParser.Cycle_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#cycle_clause.
    def exitCycle_clause(self, ctx:FirebirdParser.Cycle_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#subav_factoring_clause.
    def enterSubav_factoring_clause(self, ctx:FirebirdParser.Subav_factoring_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#subav_factoring_clause.
    def exitSubav_factoring_clause(self, ctx:FirebirdParser.Subav_factoring_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#subav_clause.
    def enterSubav_clause(self, ctx:FirebirdParser.Subav_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#subav_clause.
    def exitSubav_clause(self, ctx:FirebirdParser.Subav_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#hierarchies_clause.
    def enterHierarchies_clause(self, ctx:FirebirdParser.Hierarchies_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#hierarchies_clause.
    def exitHierarchies_clause(self, ctx:FirebirdParser.Hierarchies_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#filter_clauses.
    def enterFilter_clauses(self, ctx:FirebirdParser.Filter_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#filter_clauses.
    def exitFilter_clauses(self, ctx:FirebirdParser.Filter_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#filter_clause.
    def enterFilter_clause(self, ctx:FirebirdParser.Filter_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#filter_clause.
    def exitFilter_clause(self, ctx:FirebirdParser.Filter_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#add_calcs_clause.
    def enterAdd_calcs_clause(self, ctx:FirebirdParser.Add_calcs_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#add_calcs_clause.
    def exitAdd_calcs_clause(self, ctx:FirebirdParser.Add_calcs_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#add_calc_meas_clause.
    def enterAdd_calc_meas_clause(self, ctx:FirebirdParser.Add_calc_meas_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#add_calc_meas_clause.
    def exitAdd_calc_meas_clause(self, ctx:FirebirdParser.Add_calc_meas_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#subquery.
    def enterSubquery(self, ctx:FirebirdParser.SubqueryContext):
        pass

    # Exit a parse tree produced by FirebirdParser#subquery.
    def exitSubquery(self, ctx:FirebirdParser.SubqueryContext):
        pass


    # Enter a parse tree produced by FirebirdParser#subquery_basic_elements.
    def enterSubquery_basic_elements(self, ctx:FirebirdParser.Subquery_basic_elementsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#subquery_basic_elements.
    def exitSubquery_basic_elements(self, ctx:FirebirdParser.Subquery_basic_elementsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#subquery_operation_part.
    def enterSubquery_operation_part(self, ctx:FirebirdParser.Subquery_operation_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#subquery_operation_part.
    def exitSubquery_operation_part(self, ctx:FirebirdParser.Subquery_operation_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#query_block.
    def enterQuery_block(self, ctx:FirebirdParser.Query_blockContext):
        pass

    # Exit a parse tree produced by FirebirdParser#query_block.
    def exitQuery_block(self, ctx:FirebirdParser.Query_blockContext):
        pass


    # Enter a parse tree produced by FirebirdParser#selected_list.
    def enterSelected_list(self, ctx:FirebirdParser.Selected_listContext):
        pass

    # Exit a parse tree produced by FirebirdParser#selected_list.
    def exitSelected_list(self, ctx:FirebirdParser.Selected_listContext):
        pass


    # Enter a parse tree produced by FirebirdParser#from_clause.
    def enterFrom_clause(self, ctx:FirebirdParser.From_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#from_clause.
    def exitFrom_clause(self, ctx:FirebirdParser.From_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#select_list_elements.
    def enterSelect_list_elements(self, ctx:FirebirdParser.Select_list_elementsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#select_list_elements.
    def exitSelect_list_elements(self, ctx:FirebirdParser.Select_list_elementsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#table_ref_list.
    def enterTable_ref_list(self, ctx:FirebirdParser.Table_ref_listContext):
        pass

    # Exit a parse tree produced by FirebirdParser#table_ref_list.
    def exitTable_ref_list(self, ctx:FirebirdParser.Table_ref_listContext):
        pass


    # Enter a parse tree produced by FirebirdParser#table_ref.
    def enterTable_ref(self, ctx:FirebirdParser.Table_refContext):
        pass

    # Exit a parse tree produced by FirebirdParser#table_ref.
    def exitTable_ref(self, ctx:FirebirdParser.Table_refContext):
        pass


    # Enter a parse tree produced by FirebirdParser#table_ref_aux.
    def enterTable_ref_aux(self, ctx:FirebirdParser.Table_ref_auxContext):
        pass

    # Exit a parse tree produced by FirebirdParser#table_ref_aux.
    def exitTable_ref_aux(self, ctx:FirebirdParser.Table_ref_auxContext):
        pass


    # Enter a parse tree produced by FirebirdParser#table_ref_aux_internal_one.
    def enterTable_ref_aux_internal_one(self, ctx:FirebirdParser.Table_ref_aux_internal_oneContext):
        pass

    # Exit a parse tree produced by FirebirdParser#table_ref_aux_internal_one.
    def exitTable_ref_aux_internal_one(self, ctx:FirebirdParser.Table_ref_aux_internal_oneContext):
        pass


    # Enter a parse tree produced by FirebirdParser#table_ref_aux_internal_two.
    def enterTable_ref_aux_internal_two(self, ctx:FirebirdParser.Table_ref_aux_internal_twoContext):
        pass

    # Exit a parse tree produced by FirebirdParser#table_ref_aux_internal_two.
    def exitTable_ref_aux_internal_two(self, ctx:FirebirdParser.Table_ref_aux_internal_twoContext):
        pass


    # Enter a parse tree produced by FirebirdParser#table_ref_aux_internal_thre.
    def enterTable_ref_aux_internal_thre(self, ctx:FirebirdParser.Table_ref_aux_internal_threContext):
        pass

    # Exit a parse tree produced by FirebirdParser#table_ref_aux_internal_thre.
    def exitTable_ref_aux_internal_thre(self, ctx:FirebirdParser.Table_ref_aux_internal_threContext):
        pass


    # Enter a parse tree produced by FirebirdParser#join_clause.
    def enterJoin_clause(self, ctx:FirebirdParser.Join_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#join_clause.
    def exitJoin_clause(self, ctx:FirebirdParser.Join_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#join_on_part.
    def enterJoin_on_part(self, ctx:FirebirdParser.Join_on_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#join_on_part.
    def exitJoin_on_part(self, ctx:FirebirdParser.Join_on_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#join_using_part.
    def enterJoin_using_part(self, ctx:FirebirdParser.Join_using_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#join_using_part.
    def exitJoin_using_part(self, ctx:FirebirdParser.Join_using_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#outer_join_type.
    def enterOuter_join_type(self, ctx:FirebirdParser.Outer_join_typeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#outer_join_type.
    def exitOuter_join_type(self, ctx:FirebirdParser.Outer_join_typeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#query_partition_clause.
    def enterQuery_partition_clause(self, ctx:FirebirdParser.Query_partition_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#query_partition_clause.
    def exitQuery_partition_clause(self, ctx:FirebirdParser.Query_partition_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#flashback_query_clause.
    def enterFlashback_query_clause(self, ctx:FirebirdParser.Flashback_query_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#flashback_query_clause.
    def exitFlashback_query_clause(self, ctx:FirebirdParser.Flashback_query_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#pivot_clause.
    def enterPivot_clause(self, ctx:FirebirdParser.Pivot_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#pivot_clause.
    def exitPivot_clause(self, ctx:FirebirdParser.Pivot_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#pivot_element.
    def enterPivot_element(self, ctx:FirebirdParser.Pivot_elementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#pivot_element.
    def exitPivot_element(self, ctx:FirebirdParser.Pivot_elementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#pivot_for_clause.
    def enterPivot_for_clause(self, ctx:FirebirdParser.Pivot_for_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#pivot_for_clause.
    def exitPivot_for_clause(self, ctx:FirebirdParser.Pivot_for_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#pivot_in_clause.
    def enterPivot_in_clause(self, ctx:FirebirdParser.Pivot_in_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#pivot_in_clause.
    def exitPivot_in_clause(self, ctx:FirebirdParser.Pivot_in_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#pivot_in_clause_element.
    def enterPivot_in_clause_element(self, ctx:FirebirdParser.Pivot_in_clause_elementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#pivot_in_clause_element.
    def exitPivot_in_clause_element(self, ctx:FirebirdParser.Pivot_in_clause_elementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#pivot_in_clause_elements.
    def enterPivot_in_clause_elements(self, ctx:FirebirdParser.Pivot_in_clause_elementsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#pivot_in_clause_elements.
    def exitPivot_in_clause_elements(self, ctx:FirebirdParser.Pivot_in_clause_elementsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#unpivot_clause.
    def enterUnpivot_clause(self, ctx:FirebirdParser.Unpivot_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#unpivot_clause.
    def exitUnpivot_clause(self, ctx:FirebirdParser.Unpivot_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#unpivot_in_clause.
    def enterUnpivot_in_clause(self, ctx:FirebirdParser.Unpivot_in_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#unpivot_in_clause.
    def exitUnpivot_in_clause(self, ctx:FirebirdParser.Unpivot_in_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#unpivot_in_elements.
    def enterUnpivot_in_elements(self, ctx:FirebirdParser.Unpivot_in_elementsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#unpivot_in_elements.
    def exitUnpivot_in_elements(self, ctx:FirebirdParser.Unpivot_in_elementsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#hierarchical_query_clause.
    def enterHierarchical_query_clause(self, ctx:FirebirdParser.Hierarchical_query_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#hierarchical_query_clause.
    def exitHierarchical_query_clause(self, ctx:FirebirdParser.Hierarchical_query_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#start_part.
    def enterStart_part(self, ctx:FirebirdParser.Start_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#start_part.
    def exitStart_part(self, ctx:FirebirdParser.Start_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#group_by_clause.
    def enterGroup_by_clause(self, ctx:FirebirdParser.Group_by_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#group_by_clause.
    def exitGroup_by_clause(self, ctx:FirebirdParser.Group_by_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#group_by_elements.
    def enterGroup_by_elements(self, ctx:FirebirdParser.Group_by_elementsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#group_by_elements.
    def exitGroup_by_elements(self, ctx:FirebirdParser.Group_by_elementsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#rollup_cube_clause.
    def enterRollup_cube_clause(self, ctx:FirebirdParser.Rollup_cube_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#rollup_cube_clause.
    def exitRollup_cube_clause(self, ctx:FirebirdParser.Rollup_cube_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#grouping_sets_clause.
    def enterGrouping_sets_clause(self, ctx:FirebirdParser.Grouping_sets_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#grouping_sets_clause.
    def exitGrouping_sets_clause(self, ctx:FirebirdParser.Grouping_sets_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#grouping_sets_elements.
    def enterGrouping_sets_elements(self, ctx:FirebirdParser.Grouping_sets_elementsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#grouping_sets_elements.
    def exitGrouping_sets_elements(self, ctx:FirebirdParser.Grouping_sets_elementsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#having_clause.
    def enterHaving_clause(self, ctx:FirebirdParser.Having_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#having_clause.
    def exitHaving_clause(self, ctx:FirebirdParser.Having_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#model_clause.
    def enterModel_clause(self, ctx:FirebirdParser.Model_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#model_clause.
    def exitModel_clause(self, ctx:FirebirdParser.Model_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#cell_reference_options.
    def enterCell_reference_options(self, ctx:FirebirdParser.Cell_reference_optionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#cell_reference_options.
    def exitCell_reference_options(self, ctx:FirebirdParser.Cell_reference_optionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#return_rows_clause.
    def enterReturn_rows_clause(self, ctx:FirebirdParser.Return_rows_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#return_rows_clause.
    def exitReturn_rows_clause(self, ctx:FirebirdParser.Return_rows_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#reference_model.
    def enterReference_model(self, ctx:FirebirdParser.Reference_modelContext):
        pass

    # Exit a parse tree produced by FirebirdParser#reference_model.
    def exitReference_model(self, ctx:FirebirdParser.Reference_modelContext):
        pass


    # Enter a parse tree produced by FirebirdParser#main_model.
    def enterMain_model(self, ctx:FirebirdParser.Main_modelContext):
        pass

    # Exit a parse tree produced by FirebirdParser#main_model.
    def exitMain_model(self, ctx:FirebirdParser.Main_modelContext):
        pass


    # Enter a parse tree produced by FirebirdParser#model_column_clauses.
    def enterModel_column_clauses(self, ctx:FirebirdParser.Model_column_clausesContext):
        pass

    # Exit a parse tree produced by FirebirdParser#model_column_clauses.
    def exitModel_column_clauses(self, ctx:FirebirdParser.Model_column_clausesContext):
        pass


    # Enter a parse tree produced by FirebirdParser#model_column_partition_part.
    def enterModel_column_partition_part(self, ctx:FirebirdParser.Model_column_partition_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#model_column_partition_part.
    def exitModel_column_partition_part(self, ctx:FirebirdParser.Model_column_partition_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#model_column_list.
    def enterModel_column_list(self, ctx:FirebirdParser.Model_column_listContext):
        pass

    # Exit a parse tree produced by FirebirdParser#model_column_list.
    def exitModel_column_list(self, ctx:FirebirdParser.Model_column_listContext):
        pass


    # Enter a parse tree produced by FirebirdParser#model_column.
    def enterModel_column(self, ctx:FirebirdParser.Model_columnContext):
        pass

    # Exit a parse tree produced by FirebirdParser#model_column.
    def exitModel_column(self, ctx:FirebirdParser.Model_columnContext):
        pass


    # Enter a parse tree produced by FirebirdParser#model_rules_clause.
    def enterModel_rules_clause(self, ctx:FirebirdParser.Model_rules_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#model_rules_clause.
    def exitModel_rules_clause(self, ctx:FirebirdParser.Model_rules_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#model_rules_part.
    def enterModel_rules_part(self, ctx:FirebirdParser.Model_rules_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#model_rules_part.
    def exitModel_rules_part(self, ctx:FirebirdParser.Model_rules_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#model_rules_element.
    def enterModel_rules_element(self, ctx:FirebirdParser.Model_rules_elementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#model_rules_element.
    def exitModel_rules_element(self, ctx:FirebirdParser.Model_rules_elementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#cell_assignment.
    def enterCell_assignment(self, ctx:FirebirdParser.Cell_assignmentContext):
        pass

    # Exit a parse tree produced by FirebirdParser#cell_assignment.
    def exitCell_assignment(self, ctx:FirebirdParser.Cell_assignmentContext):
        pass


    # Enter a parse tree produced by FirebirdParser#model_iterate_clause.
    def enterModel_iterate_clause(self, ctx:FirebirdParser.Model_iterate_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#model_iterate_clause.
    def exitModel_iterate_clause(self, ctx:FirebirdParser.Model_iterate_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#until_part.
    def enterUntil_part(self, ctx:FirebirdParser.Until_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#until_part.
    def exitUntil_part(self, ctx:FirebirdParser.Until_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#order_by_clause.
    def enterOrder_by_clause(self, ctx:FirebirdParser.Order_by_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#order_by_clause.
    def exitOrder_by_clause(self, ctx:FirebirdParser.Order_by_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#order_by_elements.
    def enterOrder_by_elements(self, ctx:FirebirdParser.Order_by_elementsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#order_by_elements.
    def exitOrder_by_elements(self, ctx:FirebirdParser.Order_by_elementsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#offset_clause.
    def enterOffset_clause(self, ctx:FirebirdParser.Offset_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#offset_clause.
    def exitOffset_clause(self, ctx:FirebirdParser.Offset_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#fetch_clause.
    def enterFetch_clause(self, ctx:FirebirdParser.Fetch_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#fetch_clause.
    def exitFetch_clause(self, ctx:FirebirdParser.Fetch_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#for_update_clause.
    def enterFor_update_clause(self, ctx:FirebirdParser.For_update_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#for_update_clause.
    def exitFor_update_clause(self, ctx:FirebirdParser.For_update_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#for_update_of_part.
    def enterFor_update_of_part(self, ctx:FirebirdParser.For_update_of_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#for_update_of_part.
    def exitFor_update_of_part(self, ctx:FirebirdParser.For_update_of_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#for_update_options.
    def enterFor_update_options(self, ctx:FirebirdParser.For_update_optionsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#for_update_options.
    def exitFor_update_options(self, ctx:FirebirdParser.For_update_optionsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#update_statement.
    def enterUpdate_statement(self, ctx:FirebirdParser.Update_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#update_statement.
    def exitUpdate_statement(self, ctx:FirebirdParser.Update_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#update_set_clause.
    def enterUpdate_set_clause(self, ctx:FirebirdParser.Update_set_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#update_set_clause.
    def exitUpdate_set_clause(self, ctx:FirebirdParser.Update_set_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#column_based_update_set_clause.
    def enterColumn_based_update_set_clause(self, ctx:FirebirdParser.Column_based_update_set_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#column_based_update_set_clause.
    def exitColumn_based_update_set_clause(self, ctx:FirebirdParser.Column_based_update_set_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#delete_statement.
    def enterDelete_statement(self, ctx:FirebirdParser.Delete_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#delete_statement.
    def exitDelete_statement(self, ctx:FirebirdParser.Delete_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#insert_statement.
    def enterInsert_statement(self, ctx:FirebirdParser.Insert_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#insert_statement.
    def exitInsert_statement(self, ctx:FirebirdParser.Insert_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#single_table_insert.
    def enterSingle_table_insert(self, ctx:FirebirdParser.Single_table_insertContext):
        pass

    # Exit a parse tree produced by FirebirdParser#single_table_insert.
    def exitSingle_table_insert(self, ctx:FirebirdParser.Single_table_insertContext):
        pass


    # Enter a parse tree produced by FirebirdParser#multi_table_insert.
    def enterMulti_table_insert(self, ctx:FirebirdParser.Multi_table_insertContext):
        pass

    # Exit a parse tree produced by FirebirdParser#multi_table_insert.
    def exitMulti_table_insert(self, ctx:FirebirdParser.Multi_table_insertContext):
        pass


    # Enter a parse tree produced by FirebirdParser#multi_table_element.
    def enterMulti_table_element(self, ctx:FirebirdParser.Multi_table_elementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#multi_table_element.
    def exitMulti_table_element(self, ctx:FirebirdParser.Multi_table_elementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#conditional_insert_clause.
    def enterConditional_insert_clause(self, ctx:FirebirdParser.Conditional_insert_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#conditional_insert_clause.
    def exitConditional_insert_clause(self, ctx:FirebirdParser.Conditional_insert_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#conditional_insert_when_part.
    def enterConditional_insert_when_part(self, ctx:FirebirdParser.Conditional_insert_when_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#conditional_insert_when_part.
    def exitConditional_insert_when_part(self, ctx:FirebirdParser.Conditional_insert_when_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#conditional_insert_else_part.
    def enterConditional_insert_else_part(self, ctx:FirebirdParser.Conditional_insert_else_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#conditional_insert_else_part.
    def exitConditional_insert_else_part(self, ctx:FirebirdParser.Conditional_insert_else_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#insert_into_clause.
    def enterInsert_into_clause(self, ctx:FirebirdParser.Insert_into_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#insert_into_clause.
    def exitInsert_into_clause(self, ctx:FirebirdParser.Insert_into_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#values_clause.
    def enterValues_clause(self, ctx:FirebirdParser.Values_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#values_clause.
    def exitValues_clause(self, ctx:FirebirdParser.Values_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#merge_statement.
    def enterMerge_statement(self, ctx:FirebirdParser.Merge_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#merge_statement.
    def exitMerge_statement(self, ctx:FirebirdParser.Merge_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#merge_update_clause.
    def enterMerge_update_clause(self, ctx:FirebirdParser.Merge_update_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#merge_update_clause.
    def exitMerge_update_clause(self, ctx:FirebirdParser.Merge_update_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#merge_element.
    def enterMerge_element(self, ctx:FirebirdParser.Merge_elementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#merge_element.
    def exitMerge_element(self, ctx:FirebirdParser.Merge_elementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#merge_update_delete_part.
    def enterMerge_update_delete_part(self, ctx:FirebirdParser.Merge_update_delete_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#merge_update_delete_part.
    def exitMerge_update_delete_part(self, ctx:FirebirdParser.Merge_update_delete_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#merge_insert_clause.
    def enterMerge_insert_clause(self, ctx:FirebirdParser.Merge_insert_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#merge_insert_clause.
    def exitMerge_insert_clause(self, ctx:FirebirdParser.Merge_insert_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#selected_tableview.
    def enterSelected_tableview(self, ctx:FirebirdParser.Selected_tableviewContext):
        pass

    # Exit a parse tree produced by FirebirdParser#selected_tableview.
    def exitSelected_tableview(self, ctx:FirebirdParser.Selected_tableviewContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lock_table_statement.
    def enterLock_table_statement(self, ctx:FirebirdParser.Lock_table_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lock_table_statement.
    def exitLock_table_statement(self, ctx:FirebirdParser.Lock_table_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#wait_nowait_part.
    def enterWait_nowait_part(self, ctx:FirebirdParser.Wait_nowait_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#wait_nowait_part.
    def exitWait_nowait_part(self, ctx:FirebirdParser.Wait_nowait_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lock_table_element.
    def enterLock_table_element(self, ctx:FirebirdParser.Lock_table_elementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lock_table_element.
    def exitLock_table_element(self, ctx:FirebirdParser.Lock_table_elementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#lock_mode.
    def enterLock_mode(self, ctx:FirebirdParser.Lock_modeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#lock_mode.
    def exitLock_mode(self, ctx:FirebirdParser.Lock_modeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#general_table_ref.
    def enterGeneral_table_ref(self, ctx:FirebirdParser.General_table_refContext):
        pass

    # Exit a parse tree produced by FirebirdParser#general_table_ref.
    def exitGeneral_table_ref(self, ctx:FirebirdParser.General_table_refContext):
        pass


    # Enter a parse tree produced by FirebirdParser#static_returning_clause.
    def enterStatic_returning_clause(self, ctx:FirebirdParser.Static_returning_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#static_returning_clause.
    def exitStatic_returning_clause(self, ctx:FirebirdParser.Static_returning_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#error_logging_clause.
    def enterError_logging_clause(self, ctx:FirebirdParser.Error_logging_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#error_logging_clause.
    def exitError_logging_clause(self, ctx:FirebirdParser.Error_logging_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#error_logging_into_part.
    def enterError_logging_into_part(self, ctx:FirebirdParser.Error_logging_into_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#error_logging_into_part.
    def exitError_logging_into_part(self, ctx:FirebirdParser.Error_logging_into_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#error_logging_reject_part.
    def enterError_logging_reject_part(self, ctx:FirebirdParser.Error_logging_reject_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#error_logging_reject_part.
    def exitError_logging_reject_part(self, ctx:FirebirdParser.Error_logging_reject_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#dml_table_expression_clause.
    def enterDml_table_expression_clause(self, ctx:FirebirdParser.Dml_table_expression_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#dml_table_expression_clause.
    def exitDml_table_expression_clause(self, ctx:FirebirdParser.Dml_table_expression_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#table_collection_expression.
    def enterTable_collection_expression(self, ctx:FirebirdParser.Table_collection_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#table_collection_expression.
    def exitTable_collection_expression(self, ctx:FirebirdParser.Table_collection_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#subquery_restriction_clause.
    def enterSubquery_restriction_clause(self, ctx:FirebirdParser.Subquery_restriction_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#subquery_restriction_clause.
    def exitSubquery_restriction_clause(self, ctx:FirebirdParser.Subquery_restriction_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#sample_clause.
    def enterSample_clause(self, ctx:FirebirdParser.Sample_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#sample_clause.
    def exitSample_clause(self, ctx:FirebirdParser.Sample_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#seed_part.
    def enterSeed_part(self, ctx:FirebirdParser.Seed_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#seed_part.
    def exitSeed_part(self, ctx:FirebirdParser.Seed_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#condition.
    def enterCondition(self, ctx:FirebirdParser.ConditionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#condition.
    def exitCondition(self, ctx:FirebirdParser.ConditionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#expressions_.
    def enterExpressions_(self, ctx:FirebirdParser.Expressions_Context):
        pass

    # Exit a parse tree produced by FirebirdParser#expressions_.
    def exitExpressions_(self, ctx:FirebirdParser.Expressions_Context):
        pass


    # Enter a parse tree produced by FirebirdParser#expression.
    def enterExpression(self, ctx:FirebirdParser.ExpressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#expression.
    def exitExpression(self, ctx:FirebirdParser.ExpressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#cursor_expression.
    def enterCursor_expression(self, ctx:FirebirdParser.Cursor_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#cursor_expression.
    def exitCursor_expression(self, ctx:FirebirdParser.Cursor_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#logical_expression.
    def enterLogical_expression(self, ctx:FirebirdParser.Logical_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#logical_expression.
    def exitLogical_expression(self, ctx:FirebirdParser.Logical_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#unary_logical_expression.
    def enterUnary_logical_expression(self, ctx:FirebirdParser.Unary_logical_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#unary_logical_expression.
    def exitUnary_logical_expression(self, ctx:FirebirdParser.Unary_logical_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#unary_logical_operation.
    def enterUnary_logical_operation(self, ctx:FirebirdParser.Unary_logical_operationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#unary_logical_operation.
    def exitUnary_logical_operation(self, ctx:FirebirdParser.Unary_logical_operationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#logical_operation.
    def enterLogical_operation(self, ctx:FirebirdParser.Logical_operationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#logical_operation.
    def exitLogical_operation(self, ctx:FirebirdParser.Logical_operationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#multiset_expression.
    def enterMultiset_expression(self, ctx:FirebirdParser.Multiset_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#multiset_expression.
    def exitMultiset_expression(self, ctx:FirebirdParser.Multiset_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#relational_expression.
    def enterRelational_expression(self, ctx:FirebirdParser.Relational_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#relational_expression.
    def exitRelational_expression(self, ctx:FirebirdParser.Relational_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#compound_expression.
    def enterCompound_expression(self, ctx:FirebirdParser.Compound_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#compound_expression.
    def exitCompound_expression(self, ctx:FirebirdParser.Compound_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#relational_operator.
    def enterRelational_operator(self, ctx:FirebirdParser.Relational_operatorContext):
        pass

    # Exit a parse tree produced by FirebirdParser#relational_operator.
    def exitRelational_operator(self, ctx:FirebirdParser.Relational_operatorContext):
        pass


    # Enter a parse tree produced by FirebirdParser#in_elements.
    def enterIn_elements(self, ctx:FirebirdParser.In_elementsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#in_elements.
    def exitIn_elements(self, ctx:FirebirdParser.In_elementsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#between_elements.
    def enterBetween_elements(self, ctx:FirebirdParser.Between_elementsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#between_elements.
    def exitBetween_elements(self, ctx:FirebirdParser.Between_elementsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#concatenation.
    def enterConcatenation(self, ctx:FirebirdParser.ConcatenationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#concatenation.
    def exitConcatenation(self, ctx:FirebirdParser.ConcatenationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#interval_expression.
    def enterInterval_expression(self, ctx:FirebirdParser.Interval_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#interval_expression.
    def exitInterval_expression(self, ctx:FirebirdParser.Interval_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#model_expression.
    def enterModel_expression(self, ctx:FirebirdParser.Model_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#model_expression.
    def exitModel_expression(self, ctx:FirebirdParser.Model_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#model_expression_element.
    def enterModel_expression_element(self, ctx:FirebirdParser.Model_expression_elementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#model_expression_element.
    def exitModel_expression_element(self, ctx:FirebirdParser.Model_expression_elementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#single_column_for_loop.
    def enterSingle_column_for_loop(self, ctx:FirebirdParser.Single_column_for_loopContext):
        pass

    # Exit a parse tree produced by FirebirdParser#single_column_for_loop.
    def exitSingle_column_for_loop(self, ctx:FirebirdParser.Single_column_for_loopContext):
        pass


    # Enter a parse tree produced by FirebirdParser#multi_column_for_loop.
    def enterMulti_column_for_loop(self, ctx:FirebirdParser.Multi_column_for_loopContext):
        pass

    # Exit a parse tree produced by FirebirdParser#multi_column_for_loop.
    def exitMulti_column_for_loop(self, ctx:FirebirdParser.Multi_column_for_loopContext):
        pass


    # Enter a parse tree produced by FirebirdParser#unary_expression.
    def enterUnary_expression(self, ctx:FirebirdParser.Unary_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#unary_expression.
    def exitUnary_expression(self, ctx:FirebirdParser.Unary_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#unary_expression_core.
    def enterUnary_expression_core(self, ctx:FirebirdParser.Unary_expression_coreContext):
        pass

    # Exit a parse tree produced by FirebirdParser#unary_expression_core.
    def exitUnary_expression_core(self, ctx:FirebirdParser.Unary_expression_coreContext):
        pass


    # Enter a parse tree produced by FirebirdParser#implicit_cursor_expression.
    def enterImplicit_cursor_expression(self, ctx:FirebirdParser.Implicit_cursor_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#implicit_cursor_expression.
    def exitImplicit_cursor_expression(self, ctx:FirebirdParser.Implicit_cursor_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#collection_expression.
    def enterCollection_expression(self, ctx:FirebirdParser.Collection_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#collection_expression.
    def exitCollection_expression(self, ctx:FirebirdParser.Collection_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#case_statement.
    def enterCase_statement(self, ctx:FirebirdParser.Case_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#case_statement.
    def exitCase_statement(self, ctx:FirebirdParser.Case_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#simple_case_statement.
    def enterSimple_case_statement(self, ctx:FirebirdParser.Simple_case_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#simple_case_statement.
    def exitSimple_case_statement(self, ctx:FirebirdParser.Simple_case_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#searched_case_statement.
    def enterSearched_case_statement(self, ctx:FirebirdParser.Searched_case_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#searched_case_statement.
    def exitSearched_case_statement(self, ctx:FirebirdParser.Searched_case_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#case_when_part_statement.
    def enterCase_when_part_statement(self, ctx:FirebirdParser.Case_when_part_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#case_when_part_statement.
    def exitCase_when_part_statement(self, ctx:FirebirdParser.Case_when_part_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#case_else_part_statement.
    def enterCase_else_part_statement(self, ctx:FirebirdParser.Case_else_part_statementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#case_else_part_statement.
    def exitCase_else_part_statement(self, ctx:FirebirdParser.Case_else_part_statementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#case_expression.
    def enterCase_expression(self, ctx:FirebirdParser.Case_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#case_expression.
    def exitCase_expression(self, ctx:FirebirdParser.Case_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#simple_case_expression.
    def enterSimple_case_expression(self, ctx:FirebirdParser.Simple_case_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#simple_case_expression.
    def exitSimple_case_expression(self, ctx:FirebirdParser.Simple_case_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#searched_case_expression.
    def enterSearched_case_expression(self, ctx:FirebirdParser.Searched_case_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#searched_case_expression.
    def exitSearched_case_expression(self, ctx:FirebirdParser.Searched_case_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#case_when_part_expression.
    def enterCase_when_part_expression(self, ctx:FirebirdParser.Case_when_part_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#case_when_part_expression.
    def exitCase_when_part_expression(self, ctx:FirebirdParser.Case_when_part_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#case_else_part_expression.
    def enterCase_else_part_expression(self, ctx:FirebirdParser.Case_else_part_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#case_else_part_expression.
    def exitCase_else_part_expression(self, ctx:FirebirdParser.Case_else_part_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#atom.
    def enterAtom(self, ctx:FirebirdParser.AtomContext):
        pass

    # Exit a parse tree produced by FirebirdParser#atom.
    def exitAtom(self, ctx:FirebirdParser.AtomContext):
        pass


    # Enter a parse tree produced by FirebirdParser#quantified_expression.
    def enterQuantified_expression(self, ctx:FirebirdParser.Quantified_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#quantified_expression.
    def exitQuantified_expression(self, ctx:FirebirdParser.Quantified_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#string_function.
    def enterString_function(self, ctx:FirebirdParser.String_functionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#string_function.
    def exitString_function(self, ctx:FirebirdParser.String_functionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#standard_function.
    def enterStandard_function(self, ctx:FirebirdParser.Standard_functionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#standard_function.
    def exitStandard_function(self, ctx:FirebirdParser.Standard_functionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#json_function.
    def enterJson_function(self, ctx:FirebirdParser.Json_functionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#json_function.
    def exitJson_function(self, ctx:FirebirdParser.Json_functionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#json_object_content.
    def enterJson_object_content(self, ctx:FirebirdParser.Json_object_contentContext):
        pass

    # Exit a parse tree produced by FirebirdParser#json_object_content.
    def exitJson_object_content(self, ctx:FirebirdParser.Json_object_contentContext):
        pass


    # Enter a parse tree produced by FirebirdParser#json_object_entry.
    def enterJson_object_entry(self, ctx:FirebirdParser.Json_object_entryContext):
        pass

    # Exit a parse tree produced by FirebirdParser#json_object_entry.
    def exitJson_object_entry(self, ctx:FirebirdParser.Json_object_entryContext):
        pass


    # Enter a parse tree produced by FirebirdParser#json_table_clause.
    def enterJson_table_clause(self, ctx:FirebirdParser.Json_table_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#json_table_clause.
    def exitJson_table_clause(self, ctx:FirebirdParser.Json_table_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#json_array_element.
    def enterJson_array_element(self, ctx:FirebirdParser.Json_array_elementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#json_array_element.
    def exitJson_array_element(self, ctx:FirebirdParser.Json_array_elementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#json_on_null_clause.
    def enterJson_on_null_clause(self, ctx:FirebirdParser.Json_on_null_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#json_on_null_clause.
    def exitJson_on_null_clause(self, ctx:FirebirdParser.Json_on_null_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#json_return_clause.
    def enterJson_return_clause(self, ctx:FirebirdParser.Json_return_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#json_return_clause.
    def exitJson_return_clause(self, ctx:FirebirdParser.Json_return_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#json_transform_op.
    def enterJson_transform_op(self, ctx:FirebirdParser.Json_transform_opContext):
        pass

    # Exit a parse tree produced by FirebirdParser#json_transform_op.
    def exitJson_transform_op(self, ctx:FirebirdParser.Json_transform_opContext):
        pass


    # Enter a parse tree produced by FirebirdParser#json_column_clause.
    def enterJson_column_clause(self, ctx:FirebirdParser.Json_column_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#json_column_clause.
    def exitJson_column_clause(self, ctx:FirebirdParser.Json_column_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#json_column_definition.
    def enterJson_column_definition(self, ctx:FirebirdParser.Json_column_definitionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#json_column_definition.
    def exitJson_column_definition(self, ctx:FirebirdParser.Json_column_definitionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#json_query_returning_clause.
    def enterJson_query_returning_clause(self, ctx:FirebirdParser.Json_query_returning_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#json_query_returning_clause.
    def exitJson_query_returning_clause(self, ctx:FirebirdParser.Json_query_returning_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#json_query_return_type.
    def enterJson_query_return_type(self, ctx:FirebirdParser.Json_query_return_typeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#json_query_return_type.
    def exitJson_query_return_type(self, ctx:FirebirdParser.Json_query_return_typeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#json_query_wrapper_clause.
    def enterJson_query_wrapper_clause(self, ctx:FirebirdParser.Json_query_wrapper_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#json_query_wrapper_clause.
    def exitJson_query_wrapper_clause(self, ctx:FirebirdParser.Json_query_wrapper_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#json_query_on_error_clause.
    def enterJson_query_on_error_clause(self, ctx:FirebirdParser.Json_query_on_error_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#json_query_on_error_clause.
    def exitJson_query_on_error_clause(self, ctx:FirebirdParser.Json_query_on_error_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#json_query_on_empty_clause.
    def enterJson_query_on_empty_clause(self, ctx:FirebirdParser.Json_query_on_empty_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#json_query_on_empty_clause.
    def exitJson_query_on_empty_clause(self, ctx:FirebirdParser.Json_query_on_empty_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#json_value_return_clause.
    def enterJson_value_return_clause(self, ctx:FirebirdParser.Json_value_return_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#json_value_return_clause.
    def exitJson_value_return_clause(self, ctx:FirebirdParser.Json_value_return_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#json_value_return_type.
    def enterJson_value_return_type(self, ctx:FirebirdParser.Json_value_return_typeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#json_value_return_type.
    def exitJson_value_return_type(self, ctx:FirebirdParser.Json_value_return_typeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#json_value_on_mismatch_clause.
    def enterJson_value_on_mismatch_clause(self, ctx:FirebirdParser.Json_value_on_mismatch_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#json_value_on_mismatch_clause.
    def exitJson_value_on_mismatch_clause(self, ctx:FirebirdParser.Json_value_on_mismatch_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#literal.
    def enterLiteral(self, ctx:FirebirdParser.LiteralContext):
        pass

    # Exit a parse tree produced by FirebirdParser#literal.
    def exitLiteral(self, ctx:FirebirdParser.LiteralContext):
        pass


    # Enter a parse tree produced by FirebirdParser#numeric_function_wrapper.
    def enterNumeric_function_wrapper(self, ctx:FirebirdParser.Numeric_function_wrapperContext):
        pass

    # Exit a parse tree produced by FirebirdParser#numeric_function_wrapper.
    def exitNumeric_function_wrapper(self, ctx:FirebirdParser.Numeric_function_wrapperContext):
        pass


    # Enter a parse tree produced by FirebirdParser#numeric_function.
    def enterNumeric_function(self, ctx:FirebirdParser.Numeric_functionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#numeric_function.
    def exitNumeric_function(self, ctx:FirebirdParser.Numeric_functionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#listagg_overflow_clause.
    def enterListagg_overflow_clause(self, ctx:FirebirdParser.Listagg_overflow_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#listagg_overflow_clause.
    def exitListagg_overflow_clause(self, ctx:FirebirdParser.Listagg_overflow_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#other_function.
    def enterOther_function(self, ctx:FirebirdParser.Other_functionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#other_function.
    def exitOther_function(self, ctx:FirebirdParser.Other_functionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#over_clause_keyword.
    def enterOver_clause_keyword(self, ctx:FirebirdParser.Over_clause_keywordContext):
        pass

    # Exit a parse tree produced by FirebirdParser#over_clause_keyword.
    def exitOver_clause_keyword(self, ctx:FirebirdParser.Over_clause_keywordContext):
        pass


    # Enter a parse tree produced by FirebirdParser#within_or_over_clause_keyword.
    def enterWithin_or_over_clause_keyword(self, ctx:FirebirdParser.Within_or_over_clause_keywordContext):
        pass

    # Exit a parse tree produced by FirebirdParser#within_or_over_clause_keyword.
    def exitWithin_or_over_clause_keyword(self, ctx:FirebirdParser.Within_or_over_clause_keywordContext):
        pass


    # Enter a parse tree produced by FirebirdParser#standard_prediction_function_keyword.
    def enterStandard_prediction_function_keyword(self, ctx:FirebirdParser.Standard_prediction_function_keywordContext):
        pass

    # Exit a parse tree produced by FirebirdParser#standard_prediction_function_keyword.
    def exitStandard_prediction_function_keyword(self, ctx:FirebirdParser.Standard_prediction_function_keywordContext):
        pass


    # Enter a parse tree produced by FirebirdParser#over_clause.
    def enterOver_clause(self, ctx:FirebirdParser.Over_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#over_clause.
    def exitOver_clause(self, ctx:FirebirdParser.Over_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#windowing_clause.
    def enterWindowing_clause(self, ctx:FirebirdParser.Windowing_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#windowing_clause.
    def exitWindowing_clause(self, ctx:FirebirdParser.Windowing_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#windowing_type.
    def enterWindowing_type(self, ctx:FirebirdParser.Windowing_typeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#windowing_type.
    def exitWindowing_type(self, ctx:FirebirdParser.Windowing_typeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#windowing_elements.
    def enterWindowing_elements(self, ctx:FirebirdParser.Windowing_elementsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#windowing_elements.
    def exitWindowing_elements(self, ctx:FirebirdParser.Windowing_elementsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#using_clause.
    def enterUsing_clause(self, ctx:FirebirdParser.Using_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#using_clause.
    def exitUsing_clause(self, ctx:FirebirdParser.Using_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#using_element.
    def enterUsing_element(self, ctx:FirebirdParser.Using_elementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#using_element.
    def exitUsing_element(self, ctx:FirebirdParser.Using_elementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#assignable_element.
    def enterAssignable_element(self, ctx:FirebirdParser.Assignable_elementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#assignable_element.
    def exitAssignable_element(self, ctx:FirebirdParser.Assignable_elementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#collect_order_by_part.
    def enterCollect_order_by_part(self, ctx:FirebirdParser.Collect_order_by_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#collect_order_by_part.
    def exitCollect_order_by_part(self, ctx:FirebirdParser.Collect_order_by_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#within_or_over_part.
    def enterWithin_or_over_part(self, ctx:FirebirdParser.Within_or_over_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#within_or_over_part.
    def exitWithin_or_over_part(self, ctx:FirebirdParser.Within_or_over_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#string_delimiter.
    def enterString_delimiter(self, ctx:FirebirdParser.String_delimiterContext):
        pass

    # Exit a parse tree produced by FirebirdParser#string_delimiter.
    def exitString_delimiter(self, ctx:FirebirdParser.String_delimiterContext):
        pass


    # Enter a parse tree produced by FirebirdParser#cost_matrix_clause.
    def enterCost_matrix_clause(self, ctx:FirebirdParser.Cost_matrix_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#cost_matrix_clause.
    def exitCost_matrix_clause(self, ctx:FirebirdParser.Cost_matrix_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xml_passing_clause.
    def enterXml_passing_clause(self, ctx:FirebirdParser.Xml_passing_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xml_passing_clause.
    def exitXml_passing_clause(self, ctx:FirebirdParser.Xml_passing_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xml_attributes_clause.
    def enterXml_attributes_clause(self, ctx:FirebirdParser.Xml_attributes_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xml_attributes_clause.
    def exitXml_attributes_clause(self, ctx:FirebirdParser.Xml_attributes_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xml_namespaces_clause.
    def enterXml_namespaces_clause(self, ctx:FirebirdParser.Xml_namespaces_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xml_namespaces_clause.
    def exitXml_namespaces_clause(self, ctx:FirebirdParser.Xml_namespaces_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xml_table_column.
    def enterXml_table_column(self, ctx:FirebirdParser.Xml_table_columnContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xml_table_column.
    def exitXml_table_column(self, ctx:FirebirdParser.Xml_table_columnContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xml_general_default_part.
    def enterXml_general_default_part(self, ctx:FirebirdParser.Xml_general_default_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xml_general_default_part.
    def exitXml_general_default_part(self, ctx:FirebirdParser.Xml_general_default_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xml_multiuse_expression_element.
    def enterXml_multiuse_expression_element(self, ctx:FirebirdParser.Xml_multiuse_expression_elementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xml_multiuse_expression_element.
    def exitXml_multiuse_expression_element(self, ctx:FirebirdParser.Xml_multiuse_expression_elementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xmlroot_param_version_part.
    def enterXmlroot_param_version_part(self, ctx:FirebirdParser.Xmlroot_param_version_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xmlroot_param_version_part.
    def exitXmlroot_param_version_part(self, ctx:FirebirdParser.Xmlroot_param_version_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xmlroot_param_standalone_part.
    def enterXmlroot_param_standalone_part(self, ctx:FirebirdParser.Xmlroot_param_standalone_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xmlroot_param_standalone_part.
    def exitXmlroot_param_standalone_part(self, ctx:FirebirdParser.Xmlroot_param_standalone_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xmlserialize_param_enconding_part.
    def enterXmlserialize_param_enconding_part(self, ctx:FirebirdParser.Xmlserialize_param_enconding_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xmlserialize_param_enconding_part.
    def exitXmlserialize_param_enconding_part(self, ctx:FirebirdParser.Xmlserialize_param_enconding_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xmlserialize_param_version_part.
    def enterXmlserialize_param_version_part(self, ctx:FirebirdParser.Xmlserialize_param_version_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xmlserialize_param_version_part.
    def exitXmlserialize_param_version_part(self, ctx:FirebirdParser.Xmlserialize_param_version_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xmlserialize_param_ident_part.
    def enterXmlserialize_param_ident_part(self, ctx:FirebirdParser.Xmlserialize_param_ident_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xmlserialize_param_ident_part.
    def exitXmlserialize_param_ident_part(self, ctx:FirebirdParser.Xmlserialize_param_ident_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#annotations_clause.
    def enterAnnotations_clause(self, ctx:FirebirdParser.Annotations_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#annotations_clause.
    def exitAnnotations_clause(self, ctx:FirebirdParser.Annotations_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#annotations_list.
    def enterAnnotations_list(self, ctx:FirebirdParser.Annotations_listContext):
        pass

    # Exit a parse tree produced by FirebirdParser#annotations_list.
    def exitAnnotations_list(self, ctx:FirebirdParser.Annotations_listContext):
        pass


    # Enter a parse tree produced by FirebirdParser#annotation.
    def enterAnnotation(self, ctx:FirebirdParser.AnnotationContext):
        pass

    # Exit a parse tree produced by FirebirdParser#annotation.
    def exitAnnotation(self, ctx:FirebirdParser.AnnotationContext):
        pass


    # Enter a parse tree produced by FirebirdParser#sql_plus_command.
    def enterSql_plus_command(self, ctx:FirebirdParser.Sql_plus_commandContext):
        pass

    # Exit a parse tree produced by FirebirdParser#sql_plus_command.
    def exitSql_plus_command(self, ctx:FirebirdParser.Sql_plus_commandContext):
        pass


    # Enter a parse tree produced by FirebirdParser#start_command.
    def enterStart_command(self, ctx:FirebirdParser.Start_commandContext):
        pass

    # Exit a parse tree produced by FirebirdParser#start_command.
    def exitStart_command(self, ctx:FirebirdParser.Start_commandContext):
        pass


    # Enter a parse tree produced by FirebirdParser#sql_plus_filepath.
    def enterSql_plus_filepath(self, ctx:FirebirdParser.Sql_plus_filepathContext):
        pass

    # Exit a parse tree produced by FirebirdParser#sql_plus_filepath.
    def exitSql_plus_filepath(self, ctx:FirebirdParser.Sql_plus_filepathContext):
        pass


    # Enter a parse tree produced by FirebirdParser#whenever_command.
    def enterWhenever_command(self, ctx:FirebirdParser.Whenever_commandContext):
        pass

    # Exit a parse tree produced by FirebirdParser#whenever_command.
    def exitWhenever_command(self, ctx:FirebirdParser.Whenever_commandContext):
        pass


    # Enter a parse tree produced by FirebirdParser#set_command.
    def enterSet_command(self, ctx:FirebirdParser.Set_commandContext):
        pass

    # Exit a parse tree produced by FirebirdParser#set_command.
    def exitSet_command(self, ctx:FirebirdParser.Set_commandContext):
        pass


    # Enter a parse tree produced by FirebirdParser#timing_command.
    def enterTiming_command(self, ctx:FirebirdParser.Timing_commandContext):
        pass

    # Exit a parse tree produced by FirebirdParser#timing_command.
    def exitTiming_command(self, ctx:FirebirdParser.Timing_commandContext):
        pass


    # Enter a parse tree produced by FirebirdParser#clear_command.
    def enterClear_command(self, ctx:FirebirdParser.Clear_commandContext):
        pass

    # Exit a parse tree produced by FirebirdParser#clear_command.
    def exitClear_command(self, ctx:FirebirdParser.Clear_commandContext):
        pass


    # Enter a parse tree produced by FirebirdParser#partition_extension_clause.
    def enterPartition_extension_clause(self, ctx:FirebirdParser.Partition_extension_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#partition_extension_clause.
    def exitPartition_extension_clause(self, ctx:FirebirdParser.Partition_extension_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#column_alias.
    def enterColumn_alias(self, ctx:FirebirdParser.Column_aliasContext):
        pass

    # Exit a parse tree produced by FirebirdParser#column_alias.
    def exitColumn_alias(self, ctx:FirebirdParser.Column_aliasContext):
        pass


    # Enter a parse tree produced by FirebirdParser#table_alias.
    def enterTable_alias(self, ctx:FirebirdParser.Table_aliasContext):
        pass

    # Exit a parse tree produced by FirebirdParser#table_alias.
    def exitTable_alias(self, ctx:FirebirdParser.Table_aliasContext):
        pass


    # Enter a parse tree produced by FirebirdParser#where_clause.
    def enterWhere_clause(self, ctx:FirebirdParser.Where_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#where_clause.
    def exitWhere_clause(self, ctx:FirebirdParser.Where_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#into_clause.
    def enterInto_clause(self, ctx:FirebirdParser.Into_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#into_clause.
    def exitInto_clause(self, ctx:FirebirdParser.Into_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xml_column_name.
    def enterXml_column_name(self, ctx:FirebirdParser.Xml_column_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xml_column_name.
    def exitXml_column_name(self, ctx:FirebirdParser.Xml_column_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#cost_class_name.
    def enterCost_class_name(self, ctx:FirebirdParser.Cost_class_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#cost_class_name.
    def exitCost_class_name(self, ctx:FirebirdParser.Cost_class_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#attribute_name.
    def enterAttribute_name(self, ctx:FirebirdParser.Attribute_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#attribute_name.
    def exitAttribute_name(self, ctx:FirebirdParser.Attribute_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#savepoint_name.
    def enterSavepoint_name(self, ctx:FirebirdParser.Savepoint_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#savepoint_name.
    def exitSavepoint_name(self, ctx:FirebirdParser.Savepoint_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#rollback_segment_name.
    def enterRollback_segment_name(self, ctx:FirebirdParser.Rollback_segment_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#rollback_segment_name.
    def exitRollback_segment_name(self, ctx:FirebirdParser.Rollback_segment_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#schema_name.
    def enterSchema_name(self, ctx:FirebirdParser.Schema_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#schema_name.
    def exitSchema_name(self, ctx:FirebirdParser.Schema_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#routine_name.
    def enterRoutine_name(self, ctx:FirebirdParser.Routine_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#routine_name.
    def exitRoutine_name(self, ctx:FirebirdParser.Routine_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#package_name.
    def enterPackage_name(self, ctx:FirebirdParser.Package_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#package_name.
    def exitPackage_name(self, ctx:FirebirdParser.Package_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#implementation_type_name.
    def enterImplementation_type_name(self, ctx:FirebirdParser.Implementation_type_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#implementation_type_name.
    def exitImplementation_type_name(self, ctx:FirebirdParser.Implementation_type_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#parameter_name.
    def enterParameter_name(self, ctx:FirebirdParser.Parameter_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#parameter_name.
    def exitParameter_name(self, ctx:FirebirdParser.Parameter_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#reference_model_name.
    def enterReference_model_name(self, ctx:FirebirdParser.Reference_model_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#reference_model_name.
    def exitReference_model_name(self, ctx:FirebirdParser.Reference_model_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#main_model_name.
    def enterMain_model_name(self, ctx:FirebirdParser.Main_model_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#main_model_name.
    def exitMain_model_name(self, ctx:FirebirdParser.Main_model_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#container_tableview_name.
    def enterContainer_tableview_name(self, ctx:FirebirdParser.Container_tableview_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#container_tableview_name.
    def exitContainer_tableview_name(self, ctx:FirebirdParser.Container_tableview_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#aggregate_function_name.
    def enterAggregate_function_name(self, ctx:FirebirdParser.Aggregate_function_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#aggregate_function_name.
    def exitAggregate_function_name(self, ctx:FirebirdParser.Aggregate_function_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#query_name.
    def enterQuery_name(self, ctx:FirebirdParser.Query_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#query_name.
    def exitQuery_name(self, ctx:FirebirdParser.Query_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#grantee_name.
    def enterGrantee_name(self, ctx:FirebirdParser.Grantee_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#grantee_name.
    def exitGrantee_name(self, ctx:FirebirdParser.Grantee_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#role_name.
    def enterRole_name(self, ctx:FirebirdParser.Role_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#role_name.
    def exitRole_name(self, ctx:FirebirdParser.Role_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#constraint_name.
    def enterConstraint_name(self, ctx:FirebirdParser.Constraint_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#constraint_name.
    def exitConstraint_name(self, ctx:FirebirdParser.Constraint_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#label_name.
    def enterLabel_name(self, ctx:FirebirdParser.Label_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#label_name.
    def exitLabel_name(self, ctx:FirebirdParser.Label_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#type_name.
    def enterType_name(self, ctx:FirebirdParser.Type_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#type_name.
    def exitType_name(self, ctx:FirebirdParser.Type_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#sequence_name.
    def enterSequence_name(self, ctx:FirebirdParser.Sequence_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#sequence_name.
    def exitSequence_name(self, ctx:FirebirdParser.Sequence_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#exception_name.
    def enterException_name(self, ctx:FirebirdParser.Exception_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#exception_name.
    def exitException_name(self, ctx:FirebirdParser.Exception_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#function_name.
    def enterFunction_name(self, ctx:FirebirdParser.Function_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#function_name.
    def exitFunction_name(self, ctx:FirebirdParser.Function_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#procedure_name.
    def enterProcedure_name(self, ctx:FirebirdParser.Procedure_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#procedure_name.
    def exitProcedure_name(self, ctx:FirebirdParser.Procedure_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#trigger_name.
    def enterTrigger_name(self, ctx:FirebirdParser.Trigger_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#trigger_name.
    def exitTrigger_name(self, ctx:FirebirdParser.Trigger_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#variable_name.
    def enterVariable_name(self, ctx:FirebirdParser.Variable_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#variable_name.
    def exitVariable_name(self, ctx:FirebirdParser.Variable_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#index_name.
    def enterIndex_name(self, ctx:FirebirdParser.Index_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#index_name.
    def exitIndex_name(self, ctx:FirebirdParser.Index_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#cursor_name.
    def enterCursor_name(self, ctx:FirebirdParser.Cursor_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#cursor_name.
    def exitCursor_name(self, ctx:FirebirdParser.Cursor_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#record_name.
    def enterRecord_name(self, ctx:FirebirdParser.Record_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#record_name.
    def exitRecord_name(self, ctx:FirebirdParser.Record_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#link_name.
    def enterLink_name(self, ctx:FirebirdParser.Link_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#link_name.
    def exitLink_name(self, ctx:FirebirdParser.Link_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#local_link_name.
    def enterLocal_link_name(self, ctx:FirebirdParser.Local_link_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#local_link_name.
    def exitLocal_link_name(self, ctx:FirebirdParser.Local_link_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#connection_qualifier.
    def enterConnection_qualifier(self, ctx:FirebirdParser.Connection_qualifierContext):
        pass

    # Exit a parse tree produced by FirebirdParser#connection_qualifier.
    def exitConnection_qualifier(self, ctx:FirebirdParser.Connection_qualifierContext):
        pass


    # Enter a parse tree produced by FirebirdParser#column_name.
    def enterColumn_name(self, ctx:FirebirdParser.Column_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#column_name.
    def exitColumn_name(self, ctx:FirebirdParser.Column_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#tableview_name.
    def enterTableview_name(self, ctx:FirebirdParser.Tableview_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#tableview_name.
    def exitTableview_name(self, ctx:FirebirdParser.Tableview_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#xmltable.
    def enterXmltable(self, ctx:FirebirdParser.XmltableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#xmltable.
    def exitXmltable(self, ctx:FirebirdParser.XmltableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#char_set_name.
    def enterChar_set_name(self, ctx:FirebirdParser.Char_set_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#char_set_name.
    def exitChar_set_name(self, ctx:FirebirdParser.Char_set_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#synonym_name.
    def enterSynonym_name(self, ctx:FirebirdParser.Synonym_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#synonym_name.
    def exitSynonym_name(self, ctx:FirebirdParser.Synonym_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#schema_object_name.
    def enterSchema_object_name(self, ctx:FirebirdParser.Schema_object_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#schema_object_name.
    def exitSchema_object_name(self, ctx:FirebirdParser.Schema_object_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#dir_object_name.
    def enterDir_object_name(self, ctx:FirebirdParser.Dir_object_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#dir_object_name.
    def exitDir_object_name(self, ctx:FirebirdParser.Dir_object_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#user_object_name.
    def enterUser_object_name(self, ctx:FirebirdParser.User_object_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#user_object_name.
    def exitUser_object_name(self, ctx:FirebirdParser.User_object_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#grant_object_name.
    def enterGrant_object_name(self, ctx:FirebirdParser.Grant_object_nameContext):
        pass

    # Exit a parse tree produced by FirebirdParser#grant_object_name.
    def exitGrant_object_name(self, ctx:FirebirdParser.Grant_object_nameContext):
        pass


    # Enter a parse tree produced by FirebirdParser#column_list.
    def enterColumn_list(self, ctx:FirebirdParser.Column_listContext):
        pass

    # Exit a parse tree produced by FirebirdParser#column_list.
    def exitColumn_list(self, ctx:FirebirdParser.Column_listContext):
        pass


    # Enter a parse tree produced by FirebirdParser#paren_column_list.
    def enterParen_column_list(self, ctx:FirebirdParser.Paren_column_listContext):
        pass

    # Exit a parse tree produced by FirebirdParser#paren_column_list.
    def exitParen_column_list(self, ctx:FirebirdParser.Paren_column_listContext):
        pass


    # Enter a parse tree produced by FirebirdParser#keep_clause.
    def enterKeep_clause(self, ctx:FirebirdParser.Keep_clauseContext):
        pass

    # Exit a parse tree produced by FirebirdParser#keep_clause.
    def exitKeep_clause(self, ctx:FirebirdParser.Keep_clauseContext):
        pass


    # Enter a parse tree produced by FirebirdParser#function_argument.
    def enterFunction_argument(self, ctx:FirebirdParser.Function_argumentContext):
        pass

    # Exit a parse tree produced by FirebirdParser#function_argument.
    def exitFunction_argument(self, ctx:FirebirdParser.Function_argumentContext):
        pass


    # Enter a parse tree produced by FirebirdParser#function_argument_analytic.
    def enterFunction_argument_analytic(self, ctx:FirebirdParser.Function_argument_analyticContext):
        pass

    # Exit a parse tree produced by FirebirdParser#function_argument_analytic.
    def exitFunction_argument_analytic(self, ctx:FirebirdParser.Function_argument_analyticContext):
        pass


    # Enter a parse tree produced by FirebirdParser#function_argument_modeling.
    def enterFunction_argument_modeling(self, ctx:FirebirdParser.Function_argument_modelingContext):
        pass

    # Exit a parse tree produced by FirebirdParser#function_argument_modeling.
    def exitFunction_argument_modeling(self, ctx:FirebirdParser.Function_argument_modelingContext):
        pass


    # Enter a parse tree produced by FirebirdParser#respect_or_ignore_nulls.
    def enterRespect_or_ignore_nulls(self, ctx:FirebirdParser.Respect_or_ignore_nullsContext):
        pass

    # Exit a parse tree produced by FirebirdParser#respect_or_ignore_nulls.
    def exitRespect_or_ignore_nulls(self, ctx:FirebirdParser.Respect_or_ignore_nullsContext):
        pass


    # Enter a parse tree produced by FirebirdParser#argument.
    def enterArgument(self, ctx:FirebirdParser.ArgumentContext):
        pass

    # Exit a parse tree produced by FirebirdParser#argument.
    def exitArgument(self, ctx:FirebirdParser.ArgumentContext):
        pass


    # Enter a parse tree produced by FirebirdParser#type_spec.
    def enterType_spec(self, ctx:FirebirdParser.Type_specContext):
        pass

    # Exit a parse tree produced by FirebirdParser#type_spec.
    def exitType_spec(self, ctx:FirebirdParser.Type_specContext):
        pass


    # Enter a parse tree produced by FirebirdParser#datatype.
    def enterDatatype(self, ctx:FirebirdParser.DatatypeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#datatype.
    def exitDatatype(self, ctx:FirebirdParser.DatatypeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#precision_part.
    def enterPrecision_part(self, ctx:FirebirdParser.Precision_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#precision_part.
    def exitPrecision_part(self, ctx:FirebirdParser.Precision_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#native_datatype_element.
    def enterNative_datatype_element(self, ctx:FirebirdParser.Native_datatype_elementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#native_datatype_element.
    def exitNative_datatype_element(self, ctx:FirebirdParser.Native_datatype_elementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#bind_variable.
    def enterBind_variable(self, ctx:FirebirdParser.Bind_variableContext):
        pass

    # Exit a parse tree produced by FirebirdParser#bind_variable.
    def exitBind_variable(self, ctx:FirebirdParser.Bind_variableContext):
        pass


    # Enter a parse tree produced by FirebirdParser#general_element.
    def enterGeneral_element(self, ctx:FirebirdParser.General_elementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#general_element.
    def exitGeneral_element(self, ctx:FirebirdParser.General_elementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#general_element_part.
    def enterGeneral_element_part(self, ctx:FirebirdParser.General_element_partContext):
        pass

    # Exit a parse tree produced by FirebirdParser#general_element_part.
    def exitGeneral_element_part(self, ctx:FirebirdParser.General_element_partContext):
        pass


    # Enter a parse tree produced by FirebirdParser#table_element.
    def enterTable_element(self, ctx:FirebirdParser.Table_elementContext):
        pass

    # Exit a parse tree produced by FirebirdParser#table_element.
    def exitTable_element(self, ctx:FirebirdParser.Table_elementContext):
        pass


    # Enter a parse tree produced by FirebirdParser#object_privilege.
    def enterObject_privilege(self, ctx:FirebirdParser.Object_privilegeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#object_privilege.
    def exitObject_privilege(self, ctx:FirebirdParser.Object_privilegeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#system_privilege.
    def enterSystem_privilege(self, ctx:FirebirdParser.System_privilegeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#system_privilege.
    def exitSystem_privilege(self, ctx:FirebirdParser.System_privilegeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#constant.
    def enterConstant(self, ctx:FirebirdParser.ConstantContext):
        pass

    # Exit a parse tree produced by FirebirdParser#constant.
    def exitConstant(self, ctx:FirebirdParser.ConstantContext):
        pass


    # Enter a parse tree produced by FirebirdParser#numeric.
    def enterNumeric(self, ctx:FirebirdParser.NumericContext):
        pass

    # Exit a parse tree produced by FirebirdParser#numeric.
    def exitNumeric(self, ctx:FirebirdParser.NumericContext):
        pass


    # Enter a parse tree produced by FirebirdParser#numeric_negative.
    def enterNumeric_negative(self, ctx:FirebirdParser.Numeric_negativeContext):
        pass

    # Exit a parse tree produced by FirebirdParser#numeric_negative.
    def exitNumeric_negative(self, ctx:FirebirdParser.Numeric_negativeContext):
        pass


    # Enter a parse tree produced by FirebirdParser#quoted_string.
    def enterQuoted_string(self, ctx:FirebirdParser.Quoted_stringContext):
        pass

    # Exit a parse tree produced by FirebirdParser#quoted_string.
    def exitQuoted_string(self, ctx:FirebirdParser.Quoted_stringContext):
        pass


    # Enter a parse tree produced by FirebirdParser#identifier.
    def enterIdentifier(self, ctx:FirebirdParser.IdentifierContext):
        pass

    # Exit a parse tree produced by FirebirdParser#identifier.
    def exitIdentifier(self, ctx:FirebirdParser.IdentifierContext):
        pass


    # Enter a parse tree produced by FirebirdParser#id_expression.
    def enterId_expression(self, ctx:FirebirdParser.Id_expressionContext):
        pass

    # Exit a parse tree produced by FirebirdParser#id_expression.
    def exitId_expression(self, ctx:FirebirdParser.Id_expressionContext):
        pass


    # Enter a parse tree produced by FirebirdParser#inquiry_directive.
    def enterInquiry_directive(self, ctx:FirebirdParser.Inquiry_directiveContext):
        pass

    # Exit a parse tree produced by FirebirdParser#inquiry_directive.
    def exitInquiry_directive(self, ctx:FirebirdParser.Inquiry_directiveContext):
        pass


    # Enter a parse tree produced by FirebirdParser#outer_join_sign.
    def enterOuter_join_sign(self, ctx:FirebirdParser.Outer_join_signContext):
        pass

    # Exit a parse tree produced by FirebirdParser#outer_join_sign.
    def exitOuter_join_sign(self, ctx:FirebirdParser.Outer_join_signContext):
        pass


    # Enter a parse tree produced by FirebirdParser#regular_id.
    def enterRegular_id(self, ctx:FirebirdParser.Regular_idContext):
        pass

    # Exit a parse tree produced by FirebirdParser#regular_id.
    def exitRegular_id(self, ctx:FirebirdParser.Regular_idContext):
        pass


    # Enter a parse tree produced by FirebirdParser#non_reserved_keywords_in_18c.
    def enterNon_reserved_keywords_in_18c(self, ctx:FirebirdParser.Non_reserved_keywords_in_18cContext):
        pass

    # Exit a parse tree produced by FirebirdParser#non_reserved_keywords_in_18c.
    def exitNon_reserved_keywords_in_18c(self, ctx:FirebirdParser.Non_reserved_keywords_in_18cContext):
        pass


    # Enter a parse tree produced by FirebirdParser#non_reserved_keywords_in_12c.
    def enterNon_reserved_keywords_in_12c(self, ctx:FirebirdParser.Non_reserved_keywords_in_12cContext):
        pass

    # Exit a parse tree produced by FirebirdParser#non_reserved_keywords_in_12c.
    def exitNon_reserved_keywords_in_12c(self, ctx:FirebirdParser.Non_reserved_keywords_in_12cContext):
        pass


    # Enter a parse tree produced by FirebirdParser#non_reserved_keywords_pre12c.
    def enterNon_reserved_keywords_pre12c(self, ctx:FirebirdParser.Non_reserved_keywords_pre12cContext):
        pass

    # Exit a parse tree produced by FirebirdParser#non_reserved_keywords_pre12c.
    def exitNon_reserved_keywords_pre12c(self, ctx:FirebirdParser.Non_reserved_keywords_pre12cContext):
        pass



del FirebirdParser