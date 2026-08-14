# Generated from FirebirdParser.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .FirebirdParser import FirebirdParser
else:
    from FirebirdParser import FirebirdParser

# This class defines a complete generic visitor for a parse tree produced by FirebirdParser.

class FirebirdParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by FirebirdParser#sql_script.
    def visitSql_script(self, ctx:FirebirdParser.Sql_scriptContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#unit_statement.
    def visitUnit_statement(self, ctx:FirebirdParser.Unit_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_diskgroup.
    def visitAlter_diskgroup(self, ctx:FirebirdParser.Alter_diskgroupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#add_disk_clause.
    def visitAdd_disk_clause(self, ctx:FirebirdParser.Add_disk_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_disk_clause.
    def visitDrop_disk_clause(self, ctx:FirebirdParser.Drop_disk_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#resize_disk_clause.
    def visitResize_disk_clause(self, ctx:FirebirdParser.Resize_disk_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#replace_disk_clause.
    def visitReplace_disk_clause(self, ctx:FirebirdParser.Replace_disk_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#wait_nowait.
    def visitWait_nowait(self, ctx:FirebirdParser.Wait_nowaitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#rename_disk_clause.
    def visitRename_disk_clause(self, ctx:FirebirdParser.Rename_disk_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#disk_online_clause.
    def visitDisk_online_clause(self, ctx:FirebirdParser.Disk_online_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#disk_offline_clause.
    def visitDisk_offline_clause(self, ctx:FirebirdParser.Disk_offline_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#timeout_clause.
    def visitTimeout_clause(self, ctx:FirebirdParser.Timeout_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#rebalance_diskgroup_clause.
    def visitRebalance_diskgroup_clause(self, ctx:FirebirdParser.Rebalance_diskgroup_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#phase.
    def visitPhase(self, ctx:FirebirdParser.PhaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#check_diskgroup_clause.
    def visitCheck_diskgroup_clause(self, ctx:FirebirdParser.Check_diskgroup_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#diskgroup_template_clauses.
    def visitDiskgroup_template_clauses(self, ctx:FirebirdParser.Diskgroup_template_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#qualified_template_clause.
    def visitQualified_template_clause(self, ctx:FirebirdParser.Qualified_template_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#redundancy_clause.
    def visitRedundancy_clause(self, ctx:FirebirdParser.Redundancy_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#striping_clause.
    def visitStriping_clause(self, ctx:FirebirdParser.Striping_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#force_noforce.
    def visitForce_noforce(self, ctx:FirebirdParser.Force_noforceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#diskgroup_directory_clauses.
    def visitDiskgroup_directory_clauses(self, ctx:FirebirdParser.Diskgroup_directory_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#dir_name.
    def visitDir_name(self, ctx:FirebirdParser.Dir_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#diskgroup_alias_clauses.
    def visitDiskgroup_alias_clauses(self, ctx:FirebirdParser.Diskgroup_alias_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#diskgroup_volume_clauses.
    def visitDiskgroup_volume_clauses(self, ctx:FirebirdParser.Diskgroup_volume_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#add_volume_clause.
    def visitAdd_volume_clause(self, ctx:FirebirdParser.Add_volume_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#modify_volume_clause.
    def visitModify_volume_clause(self, ctx:FirebirdParser.Modify_volume_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#diskgroup_attributes.
    def visitDiskgroup_attributes(self, ctx:FirebirdParser.Diskgroup_attributesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_diskgroup_file_clause.
    def visitDrop_diskgroup_file_clause(self, ctx:FirebirdParser.Drop_diskgroup_file_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#convert_redundancy_clause.
    def visitConvert_redundancy_clause(self, ctx:FirebirdParser.Convert_redundancy_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#usergroup_clauses.
    def visitUsergroup_clauses(self, ctx:FirebirdParser.Usergroup_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#user_clauses.
    def visitUser_clauses(self, ctx:FirebirdParser.User_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#file_permissions_clause.
    def visitFile_permissions_clause(self, ctx:FirebirdParser.File_permissions_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#file_owner_clause.
    def visitFile_owner_clause(self, ctx:FirebirdParser.File_owner_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#scrub_clause.
    def visitScrub_clause(self, ctx:FirebirdParser.Scrub_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#quotagroup_clauses.
    def visitQuotagroup_clauses(self, ctx:FirebirdParser.Quotagroup_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#property_name.
    def visitProperty_name(self, ctx:FirebirdParser.Property_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#property_value.
    def visitProperty_value(self, ctx:FirebirdParser.Property_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#filegroup_clauses.
    def visitFilegroup_clauses(self, ctx:FirebirdParser.Filegroup_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#add_filegroup_clause.
    def visitAdd_filegroup_clause(self, ctx:FirebirdParser.Add_filegroup_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#modify_filegroup_clause.
    def visitModify_filegroup_clause(self, ctx:FirebirdParser.Modify_filegroup_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#move_to_filegroup_clause.
    def visitMove_to_filegroup_clause(self, ctx:FirebirdParser.Move_to_filegroup_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_filegroup_clause.
    def visitDrop_filegroup_clause(self, ctx:FirebirdParser.Drop_filegroup_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#quorum_regular.
    def visitQuorum_regular(self, ctx:FirebirdParser.Quorum_regularContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#undrop_disk_clause.
    def visitUndrop_disk_clause(self, ctx:FirebirdParser.Undrop_disk_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#diskgroup_availability.
    def visitDiskgroup_availability(self, ctx:FirebirdParser.Diskgroup_availabilityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#enable_disable_volume.
    def visitEnable_disable_volume(self, ctx:FirebirdParser.Enable_disable_volumeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_function.
    def visitDrop_function(self, ctx:FirebirdParser.Drop_functionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_flashback_archive.
    def visitAlter_flashback_archive(self, ctx:FirebirdParser.Alter_flashback_archiveContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_hierarchy.
    def visitAlter_hierarchy(self, ctx:FirebirdParser.Alter_hierarchyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_function.
    def visitAlter_function(self, ctx:FirebirdParser.Alter_functionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_java.
    def visitAlter_java(self, ctx:FirebirdParser.Alter_javaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#match_string.
    def visitMatch_string(self, ctx:FirebirdParser.Match_stringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_function_body.
    def visitCreate_function_body(self, ctx:FirebirdParser.Create_function_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#sql_macro_body.
    def visitSql_macro_body(self, ctx:FirebirdParser.Sql_macro_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#parallel_enable_clause.
    def visitParallel_enable_clause(self, ctx:FirebirdParser.Parallel_enable_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#partition_by_clause.
    def visitPartition_by_clause(self, ctx:FirebirdParser.Partition_by_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#result_cache_clause.
    def visitResult_cache_clause(self, ctx:FirebirdParser.Result_cache_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#accessible_by_clause.
    def visitAccessible_by_clause(self, ctx:FirebirdParser.Accessible_by_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#default_collation_clause.
    def visitDefault_collation_clause(self, ctx:FirebirdParser.Default_collation_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#aggregate_clause.
    def visitAggregate_clause(self, ctx:FirebirdParser.Aggregate_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#pipelined_using_clause.
    def visitPipelined_using_clause(self, ctx:FirebirdParser.Pipelined_using_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#accessor.
    def visitAccessor(self, ctx:FirebirdParser.AccessorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#relies_on_part.
    def visitRelies_on_part(self, ctx:FirebirdParser.Relies_on_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#streaming_clause.
    def visitStreaming_clause(self, ctx:FirebirdParser.Streaming_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_outline.
    def visitAlter_outline(self, ctx:FirebirdParser.Alter_outlineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#outline_options.
    def visitOutline_options(self, ctx:FirebirdParser.Outline_optionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_lockdown_profile.
    def visitAlter_lockdown_profile(self, ctx:FirebirdParser.Alter_lockdown_profileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lockdown_feature.
    def visitLockdown_feature(self, ctx:FirebirdParser.Lockdown_featureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lockdown_options.
    def visitLockdown_options(self, ctx:FirebirdParser.Lockdown_optionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lockdown_statements.
    def visitLockdown_statements(self, ctx:FirebirdParser.Lockdown_statementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#statement_clauses.
    def visitStatement_clauses(self, ctx:FirebirdParser.Statement_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#clause_options.
    def visitClause_options(self, ctx:FirebirdParser.Clause_optionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#option_values.
    def visitOption_values(self, ctx:FirebirdParser.Option_valuesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#string_list.
    def visitString_list(self, ctx:FirebirdParser.String_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#disable_enable.
    def visitDisable_enable(self, ctx:FirebirdParser.Disable_enableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_lockdown_profile.
    def visitDrop_lockdown_profile(self, ctx:FirebirdParser.Drop_lockdown_profileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_package.
    def visitDrop_package(self, ctx:FirebirdParser.Drop_packageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_package.
    def visitAlter_package(self, ctx:FirebirdParser.Alter_packageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_package.
    def visitCreate_package(self, ctx:FirebirdParser.Create_packageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_package_body.
    def visitCreate_package_body(self, ctx:FirebirdParser.Create_package_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#package_obj_spec.
    def visitPackage_obj_spec(self, ctx:FirebirdParser.Package_obj_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#procedure_spec.
    def visitProcedure_spec(self, ctx:FirebirdParser.Procedure_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#function_spec.
    def visitFunction_spec(self, ctx:FirebirdParser.Function_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#package_obj_body.
    def visitPackage_obj_body(self, ctx:FirebirdParser.Package_obj_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_pmem_filestore.
    def visitAlter_pmem_filestore(self, ctx:FirebirdParser.Alter_pmem_filestoreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_pmem_filestore.
    def visitDrop_pmem_filestore(self, ctx:FirebirdParser.Drop_pmem_filestoreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_procedure.
    def visitDrop_procedure(self, ctx:FirebirdParser.Drop_procedureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_procedure.
    def visitAlter_procedure(self, ctx:FirebirdParser.Alter_procedureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#function_body.
    def visitFunction_body(self, ctx:FirebirdParser.Function_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#procedure_body.
    def visitProcedure_body(self, ctx:FirebirdParser.Procedure_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_procedure_body.
    def visitCreate_procedure_body(self, ctx:FirebirdParser.Create_procedure_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_resource_cost.
    def visitAlter_resource_cost(self, ctx:FirebirdParser.Alter_resource_costContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_outline.
    def visitDrop_outline(self, ctx:FirebirdParser.Drop_outlineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_rollback_segment.
    def visitAlter_rollback_segment(self, ctx:FirebirdParser.Alter_rollback_segmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_restore_point.
    def visitDrop_restore_point(self, ctx:FirebirdParser.Drop_restore_pointContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_rollback_segment.
    def visitDrop_rollback_segment(self, ctx:FirebirdParser.Drop_rollback_segmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_role.
    def visitDrop_role(self, ctx:FirebirdParser.Drop_roleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_pmem_filestore.
    def visitCreate_pmem_filestore(self, ctx:FirebirdParser.Create_pmem_filestoreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#pmem_filestore_options.
    def visitPmem_filestore_options(self, ctx:FirebirdParser.Pmem_filestore_optionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#file_path.
    def visitFile_path(self, ctx:FirebirdParser.File_pathContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_rollback_segment.
    def visitCreate_rollback_segment(self, ctx:FirebirdParser.Create_rollback_segmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_trigger.
    def visitDrop_trigger(self, ctx:FirebirdParser.Drop_triggerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_trigger.
    def visitAlter_trigger(self, ctx:FirebirdParser.Alter_triggerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_trigger.
    def visitCreate_trigger(self, ctx:FirebirdParser.Create_triggerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#trigger_follows_clause.
    def visitTrigger_follows_clause(self, ctx:FirebirdParser.Trigger_follows_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#trigger_when_clause.
    def visitTrigger_when_clause(self, ctx:FirebirdParser.Trigger_when_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#simple_dml_trigger.
    def visitSimple_dml_trigger(self, ctx:FirebirdParser.Simple_dml_triggerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#for_each_row.
    def visitFor_each_row(self, ctx:FirebirdParser.For_each_rowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#compound_dml_trigger.
    def visitCompound_dml_trigger(self, ctx:FirebirdParser.Compound_dml_triggerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#non_dml_trigger.
    def visitNon_dml_trigger(self, ctx:FirebirdParser.Non_dml_triggerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#trigger_body.
    def visitTrigger_body(self, ctx:FirebirdParser.Trigger_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#compound_trigger_block.
    def visitCompound_trigger_block(self, ctx:FirebirdParser.Compound_trigger_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#timing_point_section.
    def visitTiming_point_section(self, ctx:FirebirdParser.Timing_point_sectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#non_dml_event.
    def visitNon_dml_event(self, ctx:FirebirdParser.Non_dml_eventContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#dml_event_clause.
    def visitDml_event_clause(self, ctx:FirebirdParser.Dml_event_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#dml_event_element.
    def visitDml_event_element(self, ctx:FirebirdParser.Dml_event_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#dml_event_nested_clause.
    def visitDml_event_nested_clause(self, ctx:FirebirdParser.Dml_event_nested_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#referencing_clause.
    def visitReferencing_clause(self, ctx:FirebirdParser.Referencing_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#referencing_element.
    def visitReferencing_element(self, ctx:FirebirdParser.Referencing_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_type.
    def visitDrop_type(self, ctx:FirebirdParser.Drop_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_type.
    def visitAlter_type(self, ctx:FirebirdParser.Alter_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#compile_type_clause.
    def visitCompile_type_clause(self, ctx:FirebirdParser.Compile_type_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#replace_type_clause.
    def visitReplace_type_clause(self, ctx:FirebirdParser.Replace_type_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_method_spec.
    def visitAlter_method_spec(self, ctx:FirebirdParser.Alter_method_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_method_element.
    def visitAlter_method_element(self, ctx:FirebirdParser.Alter_method_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_collection_clauses.
    def visitAlter_collection_clauses(self, ctx:FirebirdParser.Alter_collection_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#dependent_handling_clause.
    def visitDependent_handling_clause(self, ctx:FirebirdParser.Dependent_handling_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#dependent_exceptions_part.
    def visitDependent_exceptions_part(self, ctx:FirebirdParser.Dependent_exceptions_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_type.
    def visitCreate_type(self, ctx:FirebirdParser.Create_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#type_definition.
    def visitType_definition(self, ctx:FirebirdParser.Type_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#object_type_def.
    def visitObject_type_def(self, ctx:FirebirdParser.Object_type_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#object_as_part.
    def visitObject_as_part(self, ctx:FirebirdParser.Object_as_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#object_under_part.
    def visitObject_under_part(self, ctx:FirebirdParser.Object_under_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#nested_table_type_def.
    def visitNested_table_type_def(self, ctx:FirebirdParser.Nested_table_type_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#sqlj_object_type.
    def visitSqlj_object_type(self, ctx:FirebirdParser.Sqlj_object_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#type_body.
    def visitType_body(self, ctx:FirebirdParser.Type_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#type_body_elements.
    def visitType_body_elements(self, ctx:FirebirdParser.Type_body_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#map_order_func_declaration.
    def visitMap_order_func_declaration(self, ctx:FirebirdParser.Map_order_func_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#subprog_decl_in_type.
    def visitSubprog_decl_in_type(self, ctx:FirebirdParser.Subprog_decl_in_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#proc_decl_in_type.
    def visitProc_decl_in_type(self, ctx:FirebirdParser.Proc_decl_in_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#func_decl_in_type.
    def visitFunc_decl_in_type(self, ctx:FirebirdParser.Func_decl_in_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#constructor_declaration.
    def visitConstructor_declaration(self, ctx:FirebirdParser.Constructor_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#modifier_clause.
    def visitModifier_clause(self, ctx:FirebirdParser.Modifier_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#object_member_spec.
    def visitObject_member_spec(self, ctx:FirebirdParser.Object_member_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#sqlj_object_type_attr.
    def visitSqlj_object_type_attr(self, ctx:FirebirdParser.Sqlj_object_type_attrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#element_spec.
    def visitElement_spec(self, ctx:FirebirdParser.Element_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#element_spec_options.
    def visitElement_spec_options(self, ctx:FirebirdParser.Element_spec_optionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#subprogram_spec.
    def visitSubprogram_spec(self, ctx:FirebirdParser.Subprogram_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#overriding_subprogram_spec.
    def visitOverriding_subprogram_spec(self, ctx:FirebirdParser.Overriding_subprogram_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#overriding_function_spec.
    def visitOverriding_function_spec(self, ctx:FirebirdParser.Overriding_function_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#overriding_procedure_spec.
    def visitOverriding_procedure_spec(self, ctx:FirebirdParser.Overriding_procedure_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#type_procedure_spec.
    def visitType_procedure_spec(self, ctx:FirebirdParser.Type_procedure_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#type_function_spec.
    def visitType_function_spec(self, ctx:FirebirdParser.Type_function_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#constructor_spec.
    def visitConstructor_spec(self, ctx:FirebirdParser.Constructor_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#map_order_function_spec.
    def visitMap_order_function_spec(self, ctx:FirebirdParser.Map_order_function_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#pragma_clause.
    def visitPragma_clause(self, ctx:FirebirdParser.Pragma_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#pragma_elements.
    def visitPragma_elements(self, ctx:FirebirdParser.Pragma_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#type_elements_parameter.
    def visitType_elements_parameter(self, ctx:FirebirdParser.Type_elements_parameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_sequence.
    def visitDrop_sequence(self, ctx:FirebirdParser.Drop_sequenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_sequence.
    def visitAlter_sequence(self, ctx:FirebirdParser.Alter_sequenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_session.
    def visitAlter_session(self, ctx:FirebirdParser.Alter_sessionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_session_set_clause.
    def visitAlter_session_set_clause(self, ctx:FirebirdParser.Alter_session_set_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_sequence.
    def visitCreate_sequence(self, ctx:FirebirdParser.Create_sequenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#sequence_spec.
    def visitSequence_spec(self, ctx:FirebirdParser.Sequence_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#sequence_start_clause.
    def visitSequence_start_clause(self, ctx:FirebirdParser.Sequence_start_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_analytic_view.
    def visitCreate_analytic_view(self, ctx:FirebirdParser.Create_analytic_viewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#classification_clause.
    def visitClassification_clause(self, ctx:FirebirdParser.Classification_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#caption_clause.
    def visitCaption_clause(self, ctx:FirebirdParser.Caption_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#description_clause.
    def visitDescription_clause(self, ctx:FirebirdParser.Description_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#classification_item.
    def visitClassification_item(self, ctx:FirebirdParser.Classification_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#language.
    def visitLanguage(self, ctx:FirebirdParser.LanguageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#cav_using_clause.
    def visitCav_using_clause(self, ctx:FirebirdParser.Cav_using_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#dim_by_clause.
    def visitDim_by_clause(self, ctx:FirebirdParser.Dim_by_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#dim_key.
    def visitDim_key(self, ctx:FirebirdParser.Dim_keyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#dim_ref.
    def visitDim_ref(self, ctx:FirebirdParser.Dim_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#hier_ref.
    def visitHier_ref(self, ctx:FirebirdParser.Hier_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#measures_clause.
    def visitMeasures_clause(self, ctx:FirebirdParser.Measures_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#av_measure.
    def visitAv_measure(self, ctx:FirebirdParser.Av_measureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#base_meas_clause.
    def visitBase_meas_clause(self, ctx:FirebirdParser.Base_meas_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#meas_aggregate_clause.
    def visitMeas_aggregate_clause(self, ctx:FirebirdParser.Meas_aggregate_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#calc_meas_clause.
    def visitCalc_meas_clause(self, ctx:FirebirdParser.Calc_meas_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#default_measure_clause.
    def visitDefault_measure_clause(self, ctx:FirebirdParser.Default_measure_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#default_aggregate_clause.
    def visitDefault_aggregate_clause(self, ctx:FirebirdParser.Default_aggregate_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#cache_clause.
    def visitCache_clause(self, ctx:FirebirdParser.Cache_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#cache_specification.
    def visitCache_specification(self, ctx:FirebirdParser.Cache_specificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#levels_clause.
    def visitLevels_clause(self, ctx:FirebirdParser.Levels_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#level_specification.
    def visitLevel_specification(self, ctx:FirebirdParser.Level_specificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#level_group_type.
    def visitLevel_group_type(self, ctx:FirebirdParser.Level_group_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#fact_columns_clause.
    def visitFact_columns_clause(self, ctx:FirebirdParser.Fact_columns_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#qry_transform_clause.
    def visitQry_transform_clause(self, ctx:FirebirdParser.Qry_transform_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_attribute_dimension.
    def visitCreate_attribute_dimension(self, ctx:FirebirdParser.Create_attribute_dimensionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#ad_using_clause.
    def visitAd_using_clause(self, ctx:FirebirdParser.Ad_using_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#source_clause.
    def visitSource_clause(self, ctx:FirebirdParser.Source_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#join_path_clause.
    def visitJoin_path_clause(self, ctx:FirebirdParser.Join_path_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#join_condition.
    def visitJoin_condition(self, ctx:FirebirdParser.Join_conditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#join_condition_item.
    def visitJoin_condition_item(self, ctx:FirebirdParser.Join_condition_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#attributes_clause.
    def visitAttributes_clause(self, ctx:FirebirdParser.Attributes_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#ad_attributes_clause.
    def visitAd_attributes_clause(self, ctx:FirebirdParser.Ad_attributes_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#ad_level_clause.
    def visitAd_level_clause(self, ctx:FirebirdParser.Ad_level_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#key_clause.
    def visitKey_clause(self, ctx:FirebirdParser.Key_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alternate_key_clause.
    def visitAlternate_key_clause(self, ctx:FirebirdParser.Alternate_key_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#dim_order_clause.
    def visitDim_order_clause(self, ctx:FirebirdParser.Dim_order_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#all_clause.
    def visitAll_clause(self, ctx:FirebirdParser.All_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_audit_policy.
    def visitCreate_audit_policy(self, ctx:FirebirdParser.Create_audit_policyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#privilege_audit_clause.
    def visitPrivilege_audit_clause(self, ctx:FirebirdParser.Privilege_audit_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#action_audit_clause.
    def visitAction_audit_clause(self, ctx:FirebirdParser.Action_audit_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#system_actions.
    def visitSystem_actions(self, ctx:FirebirdParser.System_actionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#standard_actions.
    def visitStandard_actions(self, ctx:FirebirdParser.Standard_actionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#actions_clause.
    def visitActions_clause(self, ctx:FirebirdParser.Actions_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#object_action.
    def visitObject_action(self, ctx:FirebirdParser.Object_actionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#system_action.
    def visitSystem_action(self, ctx:FirebirdParser.System_actionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#component_actions.
    def visitComponent_actions(self, ctx:FirebirdParser.Component_actionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#component_action.
    def visitComponent_action(self, ctx:FirebirdParser.Component_actionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#role_audit_clause.
    def visitRole_audit_clause(self, ctx:FirebirdParser.Role_audit_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_controlfile.
    def visitCreate_controlfile(self, ctx:FirebirdParser.Create_controlfileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#controlfile_options.
    def visitControlfile_options(self, ctx:FirebirdParser.Controlfile_optionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#logfile_clause.
    def visitLogfile_clause(self, ctx:FirebirdParser.Logfile_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#character_set_clause.
    def visitCharacter_set_clause(self, ctx:FirebirdParser.Character_set_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#file_specification.
    def visitFile_specification(self, ctx:FirebirdParser.File_specificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_diskgroup.
    def visitCreate_diskgroup(self, ctx:FirebirdParser.Create_diskgroupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#qualified_disk_clause.
    def visitQualified_disk_clause(self, ctx:FirebirdParser.Qualified_disk_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_edition.
    def visitCreate_edition(self, ctx:FirebirdParser.Create_editionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_flashback_archive.
    def visitCreate_flashback_archive(self, ctx:FirebirdParser.Create_flashback_archiveContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#flashback_archive_quota.
    def visitFlashback_archive_quota(self, ctx:FirebirdParser.Flashback_archive_quotaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#flashback_archive_retention.
    def visitFlashback_archive_retention(self, ctx:FirebirdParser.Flashback_archive_retentionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_hierarchy.
    def visitCreate_hierarchy(self, ctx:FirebirdParser.Create_hierarchyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#hier_using_clause.
    def visitHier_using_clause(self, ctx:FirebirdParser.Hier_using_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#level_hier_clause.
    def visitLevel_hier_clause(self, ctx:FirebirdParser.Level_hier_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#hier_attrs_clause.
    def visitHier_attrs_clause(self, ctx:FirebirdParser.Hier_attrs_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#hier_attr_clause.
    def visitHier_attr_clause(self, ctx:FirebirdParser.Hier_attr_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#hier_attr_name.
    def visitHier_attr_name(self, ctx:FirebirdParser.Hier_attr_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_index.
    def visitCreate_index(self, ctx:FirebirdParser.Create_indexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#cluster_index_clause.
    def visitCluster_index_clause(self, ctx:FirebirdParser.Cluster_index_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#cluster_name.
    def visitCluster_name(self, ctx:FirebirdParser.Cluster_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#table_index_clause.
    def visitTable_index_clause(self, ctx:FirebirdParser.Table_index_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#bitmap_join_index_clause.
    def visitBitmap_join_index_clause(self, ctx:FirebirdParser.Bitmap_join_index_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#index_expr.
    def visitIndex_expr(self, ctx:FirebirdParser.Index_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#index_properties.
    def visitIndex_properties(self, ctx:FirebirdParser.Index_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#domain_index_clause.
    def visitDomain_index_clause(self, ctx:FirebirdParser.Domain_index_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#local_domain_index_clause.
    def visitLocal_domain_index_clause(self, ctx:FirebirdParser.Local_domain_index_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xmlindex_clause.
    def visitXmlindex_clause(self, ctx:FirebirdParser.Xmlindex_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#local_xmlindex_clause.
    def visitLocal_xmlindex_clause(self, ctx:FirebirdParser.Local_xmlindex_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#global_partitioned_index.
    def visitGlobal_partitioned_index(self, ctx:FirebirdParser.Global_partitioned_indexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#index_partitioning_clause.
    def visitIndex_partitioning_clause(self, ctx:FirebirdParser.Index_partitioning_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#index_partitioning_values_list.
    def visitIndex_partitioning_values_list(self, ctx:FirebirdParser.Index_partitioning_values_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#local_partitioned_index.
    def visitLocal_partitioned_index(self, ctx:FirebirdParser.Local_partitioned_indexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#on_range_partitioned_table.
    def visitOn_range_partitioned_table(self, ctx:FirebirdParser.On_range_partitioned_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#on_list_partitioned_table.
    def visitOn_list_partitioned_table(self, ctx:FirebirdParser.On_list_partitioned_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#partitioned_table.
    def visitPartitioned_table(self, ctx:FirebirdParser.Partitioned_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#on_hash_partitioned_table.
    def visitOn_hash_partitioned_table(self, ctx:FirebirdParser.On_hash_partitioned_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#on_hash_partitioned_clause.
    def visitOn_hash_partitioned_clause(self, ctx:FirebirdParser.On_hash_partitioned_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#on_comp_partitioned_table.
    def visitOn_comp_partitioned_table(self, ctx:FirebirdParser.On_comp_partitioned_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#on_comp_partitioned_clause.
    def visitOn_comp_partitioned_clause(self, ctx:FirebirdParser.On_comp_partitioned_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#index_subpartition_clause.
    def visitIndex_subpartition_clause(self, ctx:FirebirdParser.Index_subpartition_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#index_subpartition_subclause.
    def visitIndex_subpartition_subclause(self, ctx:FirebirdParser.Index_subpartition_subclauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#odci_parameters.
    def visitOdci_parameters(self, ctx:FirebirdParser.Odci_parametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#indextype.
    def visitIndextype(self, ctx:FirebirdParser.IndextypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_index.
    def visitAlter_index(self, ctx:FirebirdParser.Alter_indexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_index_ops_set1.
    def visitAlter_index_ops_set1(self, ctx:FirebirdParser.Alter_index_ops_set1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_index_ops_set2.
    def visitAlter_index_ops_set2(self, ctx:FirebirdParser.Alter_index_ops_set2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#visible_or_invisible.
    def visitVisible_or_invisible(self, ctx:FirebirdParser.Visible_or_invisibleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#monitoring_nomonitoring.
    def visitMonitoring_nomonitoring(self, ctx:FirebirdParser.Monitoring_nomonitoringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#rebuild_clause.
    def visitRebuild_clause(self, ctx:FirebirdParser.Rebuild_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_index_partitioning.
    def visitAlter_index_partitioning(self, ctx:FirebirdParser.Alter_index_partitioningContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#modify_index_default_attrs.
    def visitModify_index_default_attrs(self, ctx:FirebirdParser.Modify_index_default_attrsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#add_hash_index_partition.
    def visitAdd_hash_index_partition(self, ctx:FirebirdParser.Add_hash_index_partitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#coalesce_index_partition.
    def visitCoalesce_index_partition(self, ctx:FirebirdParser.Coalesce_index_partitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#modify_index_partition.
    def visitModify_index_partition(self, ctx:FirebirdParser.Modify_index_partitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#modify_index_partitions_ops.
    def visitModify_index_partitions_ops(self, ctx:FirebirdParser.Modify_index_partitions_opsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#rename_index_partition.
    def visitRename_index_partition(self, ctx:FirebirdParser.Rename_index_partitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_index_partition.
    def visitDrop_index_partition(self, ctx:FirebirdParser.Drop_index_partitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#split_index_partition.
    def visitSplit_index_partition(self, ctx:FirebirdParser.Split_index_partitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#index_partition_description.
    def visitIndex_partition_description(self, ctx:FirebirdParser.Index_partition_descriptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#modify_index_subpartition.
    def visitModify_index_subpartition(self, ctx:FirebirdParser.Modify_index_subpartitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#partition_name_old.
    def visitPartition_name_old(self, ctx:FirebirdParser.Partition_name_oldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#new_partition_name.
    def visitNew_partition_name(self, ctx:FirebirdParser.New_partition_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#new_index_name.
    def visitNew_index_name(self, ctx:FirebirdParser.New_index_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_inmemory_join_group.
    def visitAlter_inmemory_join_group(self, ctx:FirebirdParser.Alter_inmemory_join_groupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_user.
    def visitCreate_user(self, ctx:FirebirdParser.Create_userContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_user.
    def visitAlter_user(self, ctx:FirebirdParser.Alter_userContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_user.
    def visitDrop_user(self, ctx:FirebirdParser.Drop_userContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_identified_by.
    def visitAlter_identified_by(self, ctx:FirebirdParser.Alter_identified_byContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#identified_by.
    def visitIdentified_by(self, ctx:FirebirdParser.Identified_byContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#identified_other_clause.
    def visitIdentified_other_clause(self, ctx:FirebirdParser.Identified_other_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#user_tablespace_clause.
    def visitUser_tablespace_clause(self, ctx:FirebirdParser.User_tablespace_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#quota_clause.
    def visitQuota_clause(self, ctx:FirebirdParser.Quota_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#profile_clause.
    def visitProfile_clause(self, ctx:FirebirdParser.Profile_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#role_clause.
    def visitRole_clause(self, ctx:FirebirdParser.Role_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#user_default_role_clause.
    def visitUser_default_role_clause(self, ctx:FirebirdParser.User_default_role_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#password_expire_clause.
    def visitPassword_expire_clause(self, ctx:FirebirdParser.Password_expire_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#user_lock_clause.
    def visitUser_lock_clause(self, ctx:FirebirdParser.User_lock_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#user_editions_clause.
    def visitUser_editions_clause(self, ctx:FirebirdParser.User_editions_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_user_editions_clause.
    def visitAlter_user_editions_clause(self, ctx:FirebirdParser.Alter_user_editions_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#proxy_clause.
    def visitProxy_clause(self, ctx:FirebirdParser.Proxy_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#container_names.
    def visitContainer_names(self, ctx:FirebirdParser.Container_namesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#set_container_data.
    def visitSet_container_data(self, ctx:FirebirdParser.Set_container_dataContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#add_rem_container_data.
    def visitAdd_rem_container_data(self, ctx:FirebirdParser.Add_rem_container_dataContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#container_data_clause.
    def visitContainer_data_clause(self, ctx:FirebirdParser.Container_data_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#administer_key_management.
    def visitAdminister_key_management(self, ctx:FirebirdParser.Administer_key_managementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#keystore_management_clauses.
    def visitKeystore_management_clauses(self, ctx:FirebirdParser.Keystore_management_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_keystore.
    def visitCreate_keystore(self, ctx:FirebirdParser.Create_keystoreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#open_keystore.
    def visitOpen_keystore(self, ctx:FirebirdParser.Open_keystoreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#force_keystore.
    def visitForce_keystore(self, ctx:FirebirdParser.Force_keystoreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#close_keystore.
    def visitClose_keystore(self, ctx:FirebirdParser.Close_keystoreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#backup_keystore.
    def visitBackup_keystore(self, ctx:FirebirdParser.Backup_keystoreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_keystore_password.
    def visitAlter_keystore_password(self, ctx:FirebirdParser.Alter_keystore_passwordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#merge_into_new_keystore.
    def visitMerge_into_new_keystore(self, ctx:FirebirdParser.Merge_into_new_keystoreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#merge_into_existing_keystore.
    def visitMerge_into_existing_keystore(self, ctx:FirebirdParser.Merge_into_existing_keystoreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#isolate_keystore.
    def visitIsolate_keystore(self, ctx:FirebirdParser.Isolate_keystoreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#unite_keystore.
    def visitUnite_keystore(self, ctx:FirebirdParser.Unite_keystoreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#key_management_clauses.
    def visitKey_management_clauses(self, ctx:FirebirdParser.Key_management_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#set_key.
    def visitSet_key(self, ctx:FirebirdParser.Set_keyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_key.
    def visitCreate_key(self, ctx:FirebirdParser.Create_keyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#mkid.
    def visitMkid(self, ctx:FirebirdParser.MkidContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#mk.
    def visitMk(self, ctx:FirebirdParser.MkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#use_key.
    def visitUse_key(self, ctx:FirebirdParser.Use_keyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#set_key_tag.
    def visitSet_key_tag(self, ctx:FirebirdParser.Set_key_tagContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#export_keys.
    def visitExport_keys(self, ctx:FirebirdParser.Export_keysContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#import_keys.
    def visitImport_keys(self, ctx:FirebirdParser.Import_keysContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#migrate_keys.
    def visitMigrate_keys(self, ctx:FirebirdParser.Migrate_keysContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#reverse_migrate_keys.
    def visitReverse_migrate_keys(self, ctx:FirebirdParser.Reverse_migrate_keysContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#move_keys.
    def visitMove_keys(self, ctx:FirebirdParser.Move_keysContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#identified_by_store.
    def visitIdentified_by_store(self, ctx:FirebirdParser.Identified_by_storeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#using_algorithm_clause.
    def visitUsing_algorithm_clause(self, ctx:FirebirdParser.Using_algorithm_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#using_tag_clause.
    def visitUsing_tag_clause(self, ctx:FirebirdParser.Using_tag_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#secret_management_clauses.
    def visitSecret_management_clauses(self, ctx:FirebirdParser.Secret_management_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#add_update_secret.
    def visitAdd_update_secret(self, ctx:FirebirdParser.Add_update_secretContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#delete_secret.
    def visitDelete_secret(self, ctx:FirebirdParser.Delete_secretContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#add_update_secret_seps.
    def visitAdd_update_secret_seps(self, ctx:FirebirdParser.Add_update_secret_sepsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#delete_secret_seps.
    def visitDelete_secret_seps(self, ctx:FirebirdParser.Delete_secret_sepsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#zero_downtime_software_patching_clauses.
    def visitZero_downtime_software_patching_clauses(self, ctx:FirebirdParser.Zero_downtime_software_patching_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#with_backup_clause.
    def visitWith_backup_clause(self, ctx:FirebirdParser.With_backup_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#identified_by_password_clause.
    def visitIdentified_by_password_clause(self, ctx:FirebirdParser.Identified_by_password_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#keystore_password.
    def visitKeystore_password(self, ctx:FirebirdParser.Keystore_passwordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#path.
    def visitPath(self, ctx:FirebirdParser.PathContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#secret.
    def visitSecret(self, ctx:FirebirdParser.SecretContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#analyze.
    def visitAnalyze(self, ctx:FirebirdParser.AnalyzeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#partition_extention_clause.
    def visitPartition_extention_clause(self, ctx:FirebirdParser.Partition_extention_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#validation_clauses.
    def visitValidation_clauses(self, ctx:FirebirdParser.Validation_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#compute_clauses.
    def visitCompute_clauses(self, ctx:FirebirdParser.Compute_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#for_clause.
    def visitFor_clause(self, ctx:FirebirdParser.For_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#online_or_offline.
    def visitOnline_or_offline(self, ctx:FirebirdParser.Online_or_offlineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#into_clause1.
    def visitInto_clause1(self, ctx:FirebirdParser.Into_clause1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#partition_key_value.
    def visitPartition_key_value(self, ctx:FirebirdParser.Partition_key_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#subpartition_key_value.
    def visitSubpartition_key_value(self, ctx:FirebirdParser.Subpartition_key_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#associate_statistics.
    def visitAssociate_statistics(self, ctx:FirebirdParser.Associate_statisticsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#column_association.
    def visitColumn_association(self, ctx:FirebirdParser.Column_associationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#function_association.
    def visitFunction_association(self, ctx:FirebirdParser.Function_associationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#indextype_name.
    def visitIndextype_name(self, ctx:FirebirdParser.Indextype_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#using_statistics_type.
    def visitUsing_statistics_type(self, ctx:FirebirdParser.Using_statistics_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#statistics_type_name.
    def visitStatistics_type_name(self, ctx:FirebirdParser.Statistics_type_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#default_cost_clause.
    def visitDefault_cost_clause(self, ctx:FirebirdParser.Default_cost_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#cpu_cost.
    def visitCpu_cost(self, ctx:FirebirdParser.Cpu_costContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#io_cost.
    def visitIo_cost(self, ctx:FirebirdParser.Io_costContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#network_cost.
    def visitNetwork_cost(self, ctx:FirebirdParser.Network_costContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#default_selectivity_clause.
    def visitDefault_selectivity_clause(self, ctx:FirebirdParser.Default_selectivity_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#default_selectivity.
    def visitDefault_selectivity(self, ctx:FirebirdParser.Default_selectivityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#storage_table_clause.
    def visitStorage_table_clause(self, ctx:FirebirdParser.Storage_table_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#unified_auditing.
    def visitUnified_auditing(self, ctx:FirebirdParser.Unified_auditingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#policy_name.
    def visitPolicy_name(self, ctx:FirebirdParser.Policy_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#audit_traditional.
    def visitAudit_traditional(self, ctx:FirebirdParser.Audit_traditionalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#audit_direct_path.
    def visitAudit_direct_path(self, ctx:FirebirdParser.Audit_direct_pathContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#audit_container_clause.
    def visitAudit_container_clause(self, ctx:FirebirdParser.Audit_container_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#audit_operation_clause.
    def visitAudit_operation_clause(self, ctx:FirebirdParser.Audit_operation_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#auditing_by_clause.
    def visitAuditing_by_clause(self, ctx:FirebirdParser.Auditing_by_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#audit_user.
    def visitAudit_user(self, ctx:FirebirdParser.Audit_userContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#audit_schema_object_clause.
    def visitAudit_schema_object_clause(self, ctx:FirebirdParser.Audit_schema_object_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#sql_operation.
    def visitSql_operation(self, ctx:FirebirdParser.Sql_operationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#auditing_on_clause.
    def visitAuditing_on_clause(self, ctx:FirebirdParser.Auditing_on_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#model_name.
    def visitModel_name(self, ctx:FirebirdParser.Model_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#object_name.
    def visitObject_name(self, ctx:FirebirdParser.Object_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#profile_name.
    def visitProfile_name(self, ctx:FirebirdParser.Profile_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#sql_statement_shortcut.
    def visitSql_statement_shortcut(self, ctx:FirebirdParser.Sql_statement_shortcutContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_index.
    def visitDrop_index(self, ctx:FirebirdParser.Drop_indexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#disassociate_statistics.
    def visitDisassociate_statistics(self, ctx:FirebirdParser.Disassociate_statisticsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_indextype.
    def visitDrop_indextype(self, ctx:FirebirdParser.Drop_indextypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_inmemory_join_group.
    def visitDrop_inmemory_join_group(self, ctx:FirebirdParser.Drop_inmemory_join_groupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#flashback_table.
    def visitFlashback_table(self, ctx:FirebirdParser.Flashback_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#restore_point.
    def visitRestore_point(self, ctx:FirebirdParser.Restore_pointContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#purge_statement.
    def visitPurge_statement(self, ctx:FirebirdParser.Purge_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#noaudit_statement.
    def visitNoaudit_statement(self, ctx:FirebirdParser.Noaudit_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#rename_object.
    def visitRename_object(self, ctx:FirebirdParser.Rename_objectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#grant_statement.
    def visitGrant_statement(self, ctx:FirebirdParser.Grant_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#container_clause.
    def visitContainer_clause(self, ctx:FirebirdParser.Container_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#revoke_statement.
    def visitRevoke_statement(self, ctx:FirebirdParser.Revoke_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#revoke_system_privilege.
    def visitRevoke_system_privilege(self, ctx:FirebirdParser.Revoke_system_privilegeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#revokee_clause.
    def visitRevokee_clause(self, ctx:FirebirdParser.Revokee_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#revoke_object_privileges.
    def visitRevoke_object_privileges(self, ctx:FirebirdParser.Revoke_object_privilegesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#on_object_clause.
    def visitOn_object_clause(self, ctx:FirebirdParser.On_object_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#revoke_roles_from_programs.
    def visitRevoke_roles_from_programs(self, ctx:FirebirdParser.Revoke_roles_from_programsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#program_unit.
    def visitProgram_unit(self, ctx:FirebirdParser.Program_unitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_dimension.
    def visitCreate_dimension(self, ctx:FirebirdParser.Create_dimensionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_directory.
    def visitCreate_directory(self, ctx:FirebirdParser.Create_directoryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#directory_name.
    def visitDirectory_name(self, ctx:FirebirdParser.Directory_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#directory_path.
    def visitDirectory_path(self, ctx:FirebirdParser.Directory_pathContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_inmemory_join_group.
    def visitCreate_inmemory_join_group(self, ctx:FirebirdParser.Create_inmemory_join_groupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_hierarchy.
    def visitDrop_hierarchy(self, ctx:FirebirdParser.Drop_hierarchyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_library.
    def visitAlter_library(self, ctx:FirebirdParser.Alter_libraryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_java.
    def visitDrop_java(self, ctx:FirebirdParser.Drop_javaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_library.
    def visitDrop_library(self, ctx:FirebirdParser.Drop_libraryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_java.
    def visitCreate_java(self, ctx:FirebirdParser.Create_javaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_library.
    def visitCreate_library(self, ctx:FirebirdParser.Create_libraryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#plsql_library_source.
    def visitPlsql_library_source(self, ctx:FirebirdParser.Plsql_library_sourceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#credential_name.
    def visitCredential_name(self, ctx:FirebirdParser.Credential_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#library_editionable.
    def visitLibrary_editionable(self, ctx:FirebirdParser.Library_editionableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#library_debug.
    def visitLibrary_debug(self, ctx:FirebirdParser.Library_debugContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#compiler_parameters_clause.
    def visitCompiler_parameters_clause(self, ctx:FirebirdParser.Compiler_parameters_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#parameter_value.
    def visitParameter_value(self, ctx:FirebirdParser.Parameter_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#library_name.
    def visitLibrary_name(self, ctx:FirebirdParser.Library_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_dimension.
    def visitAlter_dimension(self, ctx:FirebirdParser.Alter_dimensionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#level_clause.
    def visitLevel_clause(self, ctx:FirebirdParser.Level_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#hierarchy_clause.
    def visitHierarchy_clause(self, ctx:FirebirdParser.Hierarchy_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#dimension_join_clause.
    def visitDimension_join_clause(self, ctx:FirebirdParser.Dimension_join_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#attribute_clause.
    def visitAttribute_clause(self, ctx:FirebirdParser.Attribute_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#extended_attribute_clause.
    def visitExtended_attribute_clause(self, ctx:FirebirdParser.Extended_attribute_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#column_one_or_more_sub_clause.
    def visitColumn_one_or_more_sub_clause(self, ctx:FirebirdParser.Column_one_or_more_sub_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_view.
    def visitAlter_view(self, ctx:FirebirdParser.Alter_viewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_view_editionable.
    def visitAlter_view_editionable(self, ctx:FirebirdParser.Alter_view_editionableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_view.
    def visitCreate_view(self, ctx:FirebirdParser.Create_viewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#editioning_clause.
    def visitEditioning_clause(self, ctx:FirebirdParser.Editioning_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#view_options.
    def visitView_options(self, ctx:FirebirdParser.View_optionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#view_alias_constraint.
    def visitView_alias_constraint(self, ctx:FirebirdParser.View_alias_constraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#object_view_clause.
    def visitObject_view_clause(self, ctx:FirebirdParser.Object_view_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#inline_constraint.
    def visitInline_constraint(self, ctx:FirebirdParser.Inline_constraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#inline_ref_constraint.
    def visitInline_ref_constraint(self, ctx:FirebirdParser.Inline_ref_constraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#out_of_line_ref_constraint.
    def visitOut_of_line_ref_constraint(self, ctx:FirebirdParser.Out_of_line_ref_constraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#out_of_line_constraint.
    def visitOut_of_line_constraint(self, ctx:FirebirdParser.Out_of_line_constraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#constraint_state.
    def visitConstraint_state(self, ctx:FirebirdParser.Constraint_stateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xmltype_view_clause.
    def visitXmltype_view_clause(self, ctx:FirebirdParser.Xmltype_view_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xml_schema_spec.
    def visitXml_schema_spec(self, ctx:FirebirdParser.Xml_schema_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xml_schema_url.
    def visitXml_schema_url(self, ctx:FirebirdParser.Xml_schema_urlContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#element.
    def visitElement(self, ctx:FirebirdParser.ElementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_tablespace.
    def visitAlter_tablespace(self, ctx:FirebirdParser.Alter_tablespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#datafile_tempfile_clauses.
    def visitDatafile_tempfile_clauses(self, ctx:FirebirdParser.Datafile_tempfile_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#tablespace_logging_clauses.
    def visitTablespace_logging_clauses(self, ctx:FirebirdParser.Tablespace_logging_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#tablespace_group_clause.
    def visitTablespace_group_clause(self, ctx:FirebirdParser.Tablespace_group_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#tablespace_group_name.
    def visitTablespace_group_name(self, ctx:FirebirdParser.Tablespace_group_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#tablespace_state_clauses.
    def visitTablespace_state_clauses(self, ctx:FirebirdParser.Tablespace_state_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#flashback_mode_clause.
    def visitFlashback_mode_clause(self, ctx:FirebirdParser.Flashback_mode_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#new_tablespace_name.
    def visitNew_tablespace_name(self, ctx:FirebirdParser.New_tablespace_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_tablespace.
    def visitCreate_tablespace(self, ctx:FirebirdParser.Create_tablespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#permanent_tablespace_clause.
    def visitPermanent_tablespace_clause(self, ctx:FirebirdParser.Permanent_tablespace_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#tablespace_encryption_spec.
    def visitTablespace_encryption_spec(self, ctx:FirebirdParser.Tablespace_encryption_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#logging_clause.
    def visitLogging_clause(self, ctx:FirebirdParser.Logging_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#extent_management_clause.
    def visitExtent_management_clause(self, ctx:FirebirdParser.Extent_management_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#segment_management_clause.
    def visitSegment_management_clause(self, ctx:FirebirdParser.Segment_management_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#temporary_tablespace_clause.
    def visitTemporary_tablespace_clause(self, ctx:FirebirdParser.Temporary_tablespace_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#undo_tablespace_clause.
    def visitUndo_tablespace_clause(self, ctx:FirebirdParser.Undo_tablespace_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#tablespace_retention_clause.
    def visitTablespace_retention_clause(self, ctx:FirebirdParser.Tablespace_retention_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_tablespace_set.
    def visitCreate_tablespace_set(self, ctx:FirebirdParser.Create_tablespace_setContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#permanent_tablespace_attrs.
    def visitPermanent_tablespace_attrs(self, ctx:FirebirdParser.Permanent_tablespace_attrsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#tablespace_encryption_clause.
    def visitTablespace_encryption_clause(self, ctx:FirebirdParser.Tablespace_encryption_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#default_tablespace_params.
    def visitDefault_tablespace_params(self, ctx:FirebirdParser.Default_tablespace_paramsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#default_table_compression.
    def visitDefault_table_compression(self, ctx:FirebirdParser.Default_table_compressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#low_high.
    def visitLow_high(self, ctx:FirebirdParser.Low_highContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#default_index_compression.
    def visitDefault_index_compression(self, ctx:FirebirdParser.Default_index_compressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#inmmemory_clause.
    def visitInmmemory_clause(self, ctx:FirebirdParser.Inmmemory_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#datafile_specification.
    def visitDatafile_specification(self, ctx:FirebirdParser.Datafile_specificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#tempfile_specification.
    def visitTempfile_specification(self, ctx:FirebirdParser.Tempfile_specificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#datafile_tempfile_spec.
    def visitDatafile_tempfile_spec(self, ctx:FirebirdParser.Datafile_tempfile_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#redo_log_file_spec.
    def visitRedo_log_file_spec(self, ctx:FirebirdParser.Redo_log_file_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#autoextend_clause.
    def visitAutoextend_clause(self, ctx:FirebirdParser.Autoextend_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#maxsize_clause.
    def visitMaxsize_clause(self, ctx:FirebirdParser.Maxsize_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#build_clause.
    def visitBuild_clause(self, ctx:FirebirdParser.Build_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#parallel_clause.
    def visitParallel_clause(self, ctx:FirebirdParser.Parallel_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#parallel_instances_clause.
    def visitParallel_instances_clause(self, ctx:FirebirdParser.Parallel_instances_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_materialized_view.
    def visitAlter_materialized_view(self, ctx:FirebirdParser.Alter_materialized_viewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_mv_option1.
    def visitAlter_mv_option1(self, ctx:FirebirdParser.Alter_mv_option1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_mv_refresh.
    def visitAlter_mv_refresh(self, ctx:FirebirdParser.Alter_mv_refreshContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#rollback_segment.
    def visitRollback_segment(self, ctx:FirebirdParser.Rollback_segmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#modify_mv_column_clause.
    def visitModify_mv_column_clause(self, ctx:FirebirdParser.Modify_mv_column_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_materialized_view_log.
    def visitAlter_materialized_view_log(self, ctx:FirebirdParser.Alter_materialized_view_logContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#add_mv_log_column_clause.
    def visitAdd_mv_log_column_clause(self, ctx:FirebirdParser.Add_mv_log_column_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#move_mv_log_clause.
    def visitMove_mv_log_clause(self, ctx:FirebirdParser.Move_mv_log_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#mv_log_augmentation.
    def visitMv_log_augmentation(self, ctx:FirebirdParser.Mv_log_augmentationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_materialized_view_log.
    def visitCreate_materialized_view_log(self, ctx:FirebirdParser.Create_materialized_view_logContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#new_values_clause.
    def visitNew_values_clause(self, ctx:FirebirdParser.New_values_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#mv_log_purge_clause.
    def visitMv_log_purge_clause(self, ctx:FirebirdParser.Mv_log_purge_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_materialized_zonemap.
    def visitCreate_materialized_zonemap(self, ctx:FirebirdParser.Create_materialized_zonemapContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_materialized_zonemap.
    def visitAlter_materialized_zonemap(self, ctx:FirebirdParser.Alter_materialized_zonemapContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_materialized_zonemap.
    def visitDrop_materialized_zonemap(self, ctx:FirebirdParser.Drop_materialized_zonemapContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#zonemap_refresh_clause.
    def visitZonemap_refresh_clause(self, ctx:FirebirdParser.Zonemap_refresh_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#zonemap_attributes.
    def visitZonemap_attributes(self, ctx:FirebirdParser.Zonemap_attributesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#zonemap_name.
    def visitZonemap_name(self, ctx:FirebirdParser.Zonemap_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#operator_name.
    def visitOperator_name(self, ctx:FirebirdParser.Operator_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#operator_function_name.
    def visitOperator_function_name(self, ctx:FirebirdParser.Operator_function_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_zonemap_on_table.
    def visitCreate_zonemap_on_table(self, ctx:FirebirdParser.Create_zonemap_on_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_zonemap_as_subquery.
    def visitCreate_zonemap_as_subquery(self, ctx:FirebirdParser.Create_zonemap_as_subqueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_operator.
    def visitAlter_operator(self, ctx:FirebirdParser.Alter_operatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_operator.
    def visitDrop_operator(self, ctx:FirebirdParser.Drop_operatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_operator.
    def visitCreate_operator(self, ctx:FirebirdParser.Create_operatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#binding_clause.
    def visitBinding_clause(self, ctx:FirebirdParser.Binding_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#add_binding_clause.
    def visitAdd_binding_clause(self, ctx:FirebirdParser.Add_binding_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#implementation_clause.
    def visitImplementation_clause(self, ctx:FirebirdParser.Implementation_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#primary_operator_list.
    def visitPrimary_operator_list(self, ctx:FirebirdParser.Primary_operator_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#primary_operator_item.
    def visitPrimary_operator_item(self, ctx:FirebirdParser.Primary_operator_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#operator_context_clause.
    def visitOperator_context_clause(self, ctx:FirebirdParser.Operator_context_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#using_function_clause.
    def visitUsing_function_clause(self, ctx:FirebirdParser.Using_function_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_binding_clause.
    def visitDrop_binding_clause(self, ctx:FirebirdParser.Drop_binding_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_materialized_view.
    def visitCreate_materialized_view(self, ctx:FirebirdParser.Create_materialized_viewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#scoped_table_ref_constraint.
    def visitScoped_table_ref_constraint(self, ctx:FirebirdParser.Scoped_table_ref_constraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#mv_column_alias.
    def visitMv_column_alias(self, ctx:FirebirdParser.Mv_column_aliasContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_mv_refresh.
    def visitCreate_mv_refresh(self, ctx:FirebirdParser.Create_mv_refreshContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#query_rewrite_clause.
    def visitQuery_rewrite_clause(self, ctx:FirebirdParser.Query_rewrite_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#unusable_editions_clause.
    def visitUnusable_editions_clause(self, ctx:FirebirdParser.Unusable_editions_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_materialized_view.
    def visitDrop_materialized_view(self, ctx:FirebirdParser.Drop_materialized_viewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_materialized_view_log.
    def visitDrop_materialized_view_log(self, ctx:FirebirdParser.Drop_materialized_view_logContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_context.
    def visitCreate_context(self, ctx:FirebirdParser.Create_contextContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#firebird_namespace.
    def visitFirebird_namespace(self, ctx:FirebirdParser.Firebird_namespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_cluster.
    def visitCreate_cluster(self, ctx:FirebirdParser.Create_clusterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_profile.
    def visitCreate_profile(self, ctx:FirebirdParser.Create_profileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#resource_parameters.
    def visitResource_parameters(self, ctx:FirebirdParser.Resource_parametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#password_parameters.
    def visitPassword_parameters(self, ctx:FirebirdParser.Password_parametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_lockdown_profile.
    def visitCreate_lockdown_profile(self, ctx:FirebirdParser.Create_lockdown_profileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#static_base_profile.
    def visitStatic_base_profile(self, ctx:FirebirdParser.Static_base_profileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#dynamic_base_profile.
    def visitDynamic_base_profile(self, ctx:FirebirdParser.Dynamic_base_profileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_outline.
    def visitCreate_outline(self, ctx:FirebirdParser.Create_outlineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_restore_point.
    def visitCreate_restore_point(self, ctx:FirebirdParser.Create_restore_pointContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_role.
    def visitCreate_role(self, ctx:FirebirdParser.Create_roleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_table.
    def visitCreate_table(self, ctx:FirebirdParser.Create_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xmltype_table.
    def visitXmltype_table(self, ctx:FirebirdParser.Xmltype_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xmltype_virtual_columns.
    def visitXmltype_virtual_columns(self, ctx:FirebirdParser.Xmltype_virtual_columnsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xmltype_column_properties.
    def visitXmltype_column_properties(self, ctx:FirebirdParser.Xmltype_column_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xmltype_storage.
    def visitXmltype_storage(self, ctx:FirebirdParser.Xmltype_storageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xmlschema_spec.
    def visitXmlschema_spec(self, ctx:FirebirdParser.Xmlschema_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#object_table.
    def visitObject_table(self, ctx:FirebirdParser.Object_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#object_type.
    def visitObject_type(self, ctx:FirebirdParser.Object_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#oid_index_clause.
    def visitOid_index_clause(self, ctx:FirebirdParser.Oid_index_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#oid_clause.
    def visitOid_clause(self, ctx:FirebirdParser.Oid_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#object_properties.
    def visitObject_properties(self, ctx:FirebirdParser.Object_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#object_table_substitution.
    def visitObject_table_substitution(self, ctx:FirebirdParser.Object_table_substitutionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#relational_table.
    def visitRelational_table(self, ctx:FirebirdParser.Relational_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#relational_table_properties.
    def visitRelational_table_properties(self, ctx:FirebirdParser.Relational_table_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#relational_table_property.
    def visitRelational_table_property(self, ctx:FirebirdParser.Relational_table_propertyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#immutable_table_clauses.
    def visitImmutable_table_clauses(self, ctx:FirebirdParser.Immutable_table_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#immutable_table_no_drop_clause.
    def visitImmutable_table_no_drop_clause(self, ctx:FirebirdParser.Immutable_table_no_drop_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#immutable_table_no_delete_clause.
    def visitImmutable_table_no_delete_clause(self, ctx:FirebirdParser.Immutable_table_no_delete_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#blockchain_table_clauses.
    def visitBlockchain_table_clauses(self, ctx:FirebirdParser.Blockchain_table_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#blockchain_drop_table_clause.
    def visitBlockchain_drop_table_clause(self, ctx:FirebirdParser.Blockchain_drop_table_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#blockchain_row_retention_clause.
    def visitBlockchain_row_retention_clause(self, ctx:FirebirdParser.Blockchain_row_retention_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#blockchain_hash_and_data_format_clause.
    def visitBlockchain_hash_and_data_format_clause(self, ctx:FirebirdParser.Blockchain_hash_and_data_format_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#collation_name.
    def visitCollation_name(self, ctx:FirebirdParser.Collation_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#table_properties.
    def visitTable_properties(self, ctx:FirebirdParser.Table_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#read_only_clause.
    def visitRead_only_clause(self, ctx:FirebirdParser.Read_only_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#indexing_clause.
    def visitIndexing_clause(self, ctx:FirebirdParser.Indexing_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#attribute_clustering_clause.
    def visitAttribute_clustering_clause(self, ctx:FirebirdParser.Attribute_clustering_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#clustering_join.
    def visitClustering_join(self, ctx:FirebirdParser.Clustering_joinContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#clustering_join_item.
    def visitClustering_join_item(self, ctx:FirebirdParser.Clustering_join_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#equijoin_condition.
    def visitEquijoin_condition(self, ctx:FirebirdParser.Equijoin_conditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#cluster_clause.
    def visitCluster_clause(self, ctx:FirebirdParser.Cluster_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#clustering_columns.
    def visitClustering_columns(self, ctx:FirebirdParser.Clustering_columnsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#clustering_column_group.
    def visitClustering_column_group(self, ctx:FirebirdParser.Clustering_column_groupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#yes_no.
    def visitYes_no(self, ctx:FirebirdParser.Yes_noContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#zonemap_clause.
    def visitZonemap_clause(self, ctx:FirebirdParser.Zonemap_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#logical_replication_clause.
    def visitLogical_replication_clause(self, ctx:FirebirdParser.Logical_replication_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#table_name.
    def visitTable_name(self, ctx:FirebirdParser.Table_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#relational_property.
    def visitRelational_property(self, ctx:FirebirdParser.Relational_propertyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#table_partitioning_clauses.
    def visitTable_partitioning_clauses(self, ctx:FirebirdParser.Table_partitioning_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#range_partitions.
    def visitRange_partitions(self, ctx:FirebirdParser.Range_partitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#list_partitions.
    def visitList_partitions(self, ctx:FirebirdParser.List_partitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#hash_partitions.
    def visitHash_partitions(self, ctx:FirebirdParser.Hash_partitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#individual_hash_partitions.
    def visitIndividual_hash_partitions(self, ctx:FirebirdParser.Individual_hash_partitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#hash_partitions_by_quantity.
    def visitHash_partitions_by_quantity(self, ctx:FirebirdParser.Hash_partitions_by_quantityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#hash_partition_quantity.
    def visitHash_partition_quantity(self, ctx:FirebirdParser.Hash_partition_quantityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#composite_range_partitions.
    def visitComposite_range_partitions(self, ctx:FirebirdParser.Composite_range_partitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#composite_list_partitions.
    def visitComposite_list_partitions(self, ctx:FirebirdParser.Composite_list_partitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#composite_hash_partitions.
    def visitComposite_hash_partitions(self, ctx:FirebirdParser.Composite_hash_partitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#reference_partitioning.
    def visitReference_partitioning(self, ctx:FirebirdParser.Reference_partitioningContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#reference_partition_desc.
    def visitReference_partition_desc(self, ctx:FirebirdParser.Reference_partition_descContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#system_partitioning.
    def visitSystem_partitioning(self, ctx:FirebirdParser.System_partitioningContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#range_partition_desc.
    def visitRange_partition_desc(self, ctx:FirebirdParser.Range_partition_descContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#list_partition_desc.
    def visitList_partition_desc(self, ctx:FirebirdParser.List_partition_descContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#subpartition_template.
    def visitSubpartition_template(self, ctx:FirebirdParser.Subpartition_templateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#hash_subpartition_quantity.
    def visitHash_subpartition_quantity(self, ctx:FirebirdParser.Hash_subpartition_quantityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#subpartition_by_range.
    def visitSubpartition_by_range(self, ctx:FirebirdParser.Subpartition_by_rangeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#subpartition_by_list.
    def visitSubpartition_by_list(self, ctx:FirebirdParser.Subpartition_by_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#subpartition_by_hash.
    def visitSubpartition_by_hash(self, ctx:FirebirdParser.Subpartition_by_hashContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#subpartition_name.
    def visitSubpartition_name(self, ctx:FirebirdParser.Subpartition_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#range_subpartition_desc.
    def visitRange_subpartition_desc(self, ctx:FirebirdParser.Range_subpartition_descContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#list_subpartition_desc.
    def visitList_subpartition_desc(self, ctx:FirebirdParser.List_subpartition_descContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#individual_hash_subparts.
    def visitIndividual_hash_subparts(self, ctx:FirebirdParser.Individual_hash_subpartsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#hash_subparts_by_quantity.
    def visitHash_subparts_by_quantity(self, ctx:FirebirdParser.Hash_subparts_by_quantityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#range_values_clause.
    def visitRange_values_clause(self, ctx:FirebirdParser.Range_values_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#range_values_list.
    def visitRange_values_list(self, ctx:FirebirdParser.Range_values_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#list_values_clause.
    def visitList_values_clause(self, ctx:FirebirdParser.List_values_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#table_partition_description.
    def visitTable_partition_description(self, ctx:FirebirdParser.Table_partition_descriptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#partitioning_storage_clause.
    def visitPartitioning_storage_clause(self, ctx:FirebirdParser.Partitioning_storage_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lob_partitioning_storage.
    def visitLob_partitioning_storage(self, ctx:FirebirdParser.Lob_partitioning_storageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#size_clause.
    def visitSize_clause(self, ctx:FirebirdParser.Size_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#table_compression.
    def visitTable_compression(self, ctx:FirebirdParser.Table_compressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#inmemory_table_clause.
    def visitInmemory_table_clause(self, ctx:FirebirdParser.Inmemory_table_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#inmemory_attributes.
    def visitInmemory_attributes(self, ctx:FirebirdParser.Inmemory_attributesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#inmemory_memcompress.
    def visitInmemory_memcompress(self, ctx:FirebirdParser.Inmemory_memcompressContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#inmemory_priority.
    def visitInmemory_priority(self, ctx:FirebirdParser.Inmemory_priorityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#inmemory_distribute.
    def visitInmemory_distribute(self, ctx:FirebirdParser.Inmemory_distributeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#inmemory_duplicate.
    def visitInmemory_duplicate(self, ctx:FirebirdParser.Inmemory_duplicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#inmemory_column_clause.
    def visitInmemory_column_clause(self, ctx:FirebirdParser.Inmemory_column_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#physical_attributes_clause.
    def visitPhysical_attributes_clause(self, ctx:FirebirdParser.Physical_attributes_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#storage_clause.
    def visitStorage_clause(self, ctx:FirebirdParser.Storage_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#deferred_segment_creation.
    def visitDeferred_segment_creation(self, ctx:FirebirdParser.Deferred_segment_creationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#segment_attributes_clause.
    def visitSegment_attributes_clause(self, ctx:FirebirdParser.Segment_attributes_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#physical_properties.
    def visitPhysical_properties(self, ctx:FirebirdParser.Physical_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#ilm_clause.
    def visitIlm_clause(self, ctx:FirebirdParser.Ilm_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#ilm_policy_clause.
    def visitIlm_policy_clause(self, ctx:FirebirdParser.Ilm_policy_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#ilm_compression_policy.
    def visitIlm_compression_policy(self, ctx:FirebirdParser.Ilm_compression_policyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#ilm_tiering_policy.
    def visitIlm_tiering_policy(self, ctx:FirebirdParser.Ilm_tiering_policyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#ilm_after_on.
    def visitIlm_after_on(self, ctx:FirebirdParser.Ilm_after_onContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#segment_group.
    def visitSegment_group(self, ctx:FirebirdParser.Segment_groupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#ilm_inmemory_policy.
    def visitIlm_inmemory_policy(self, ctx:FirebirdParser.Ilm_inmemory_policyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#ilm_time_period.
    def visitIlm_time_period(self, ctx:FirebirdParser.Ilm_time_periodContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#heap_org_table_clause.
    def visitHeap_org_table_clause(self, ctx:FirebirdParser.Heap_org_table_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_clause.
    def visitExternal_table_clause(self, ctx:FirebirdParser.External_table_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#access_driver_type.
    def visitAccess_driver_type(self, ctx:FirebirdParser.Access_driver_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_data_props.
    def visitExternal_table_data_props(self, ctx:FirebirdParser.External_table_data_propsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_data_format.
    def visitExternal_table_data_format(self, ctx:FirebirdParser.External_table_data_formatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_transform.
    def visitExternal_table_transform(self, ctx:FirebirdParser.External_table_transformContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_field.
    def visitExternal_table_field(self, ctx:FirebirdParser.External_table_fieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_field_list.
    def visitExternal_table_field_list(self, ctx:FirebirdParser.External_table_field_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_fields_clause.
    def visitExternal_table_fields_clause(self, ctx:FirebirdParser.External_table_fields_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_position_clause.
    def visitExternal_table_position_clause(self, ctx:FirebirdParser.External_table_position_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_datatype_clause.
    def visitExternal_table_datatype_clause(self, ctx:FirebirdParser.External_table_datatype_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_delimit_clause.
    def visitExternal_table_delimit_clause(self, ctx:FirebirdParser.External_table_delimit_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_trim_clause.
    def visitExternal_table_trim_clause(self, ctx:FirebirdParser.External_table_trim_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_date_format_clause.
    def visitExternal_table_date_format_clause(self, ctx:FirebirdParser.External_table_date_format_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_init_clause.
    def visitExternal_table_init_clause(self, ctx:FirebirdParser.External_table_init_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_condition_clause.
    def visitExternal_table_condition_clause(self, ctx:FirebirdParser.External_table_condition_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_lls_clause.
    def visitExternal_table_lls_clause(self, ctx:FirebirdParser.External_table_lls_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_records.
    def visitExternal_table_records(self, ctx:FirebirdParser.External_table_recordsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_record_options_clause.
    def visitExternal_table_record_options_clause(self, ctx:FirebirdParser.External_table_record_options_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_output_files.
    def visitExternal_table_output_files(self, ctx:FirebirdParser.External_table_output_filesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_fields.
    def visitExternal_table_fields(self, ctx:FirebirdParser.External_table_fieldsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_datapump.
    def visitExternal_table_datapump(self, ctx:FirebirdParser.External_table_datapumpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_hive.
    def visitExternal_table_hive(self, ctx:FirebirdParser.External_table_hiveContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_hive_parameter_map.
    def visitExternal_table_hive_parameter_map(self, ctx:FirebirdParser.External_table_hive_parameter_mapContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_hive_parameter_map_entry.
    def visitExternal_table_hive_parameter_map_entry(self, ctx:FirebirdParser.External_table_hive_parameter_map_entryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#external_table_directory.
    def visitExternal_table_directory(self, ctx:FirebirdParser.External_table_directoryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#row_movement_clause.
    def visitRow_movement_clause(self, ctx:FirebirdParser.Row_movement_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#flashback_archive_clause.
    def visitFlashback_archive_clause(self, ctx:FirebirdParser.Flashback_archive_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#log_grp.
    def visitLog_grp(self, ctx:FirebirdParser.Log_grpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#supplemental_table_logging.
    def visitSupplemental_table_logging(self, ctx:FirebirdParser.Supplemental_table_loggingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#supplemental_log_grp_clause.
    def visitSupplemental_log_grp_clause(self, ctx:FirebirdParser.Supplemental_log_grp_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#supplemental_id_key_clause.
    def visitSupplemental_id_key_clause(self, ctx:FirebirdParser.Supplemental_id_key_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#allocate_extent_clause.
    def visitAllocate_extent_clause(self, ctx:FirebirdParser.Allocate_extent_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#deallocate_unused_clause.
    def visitDeallocate_unused_clause(self, ctx:FirebirdParser.Deallocate_unused_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#shrink_clause.
    def visitShrink_clause(self, ctx:FirebirdParser.Shrink_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#records_per_block_clause.
    def visitRecords_per_block_clause(self, ctx:FirebirdParser.Records_per_block_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#upgrade_table_clause.
    def visitUpgrade_table_clause(self, ctx:FirebirdParser.Upgrade_table_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#truncate_table.
    def visitTruncate_table(self, ctx:FirebirdParser.Truncate_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_table.
    def visitDrop_table(self, ctx:FirebirdParser.Drop_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_tablespace.
    def visitDrop_tablespace(self, ctx:FirebirdParser.Drop_tablespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_tablespace_set.
    def visitDrop_tablespace_set(self, ctx:FirebirdParser.Drop_tablespace_setContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#including_contents_clause.
    def visitIncluding_contents_clause(self, ctx:FirebirdParser.Including_contents_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_view.
    def visitDrop_view(self, ctx:FirebirdParser.Drop_viewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#comment_on_column.
    def visitComment_on_column(self, ctx:FirebirdParser.Comment_on_columnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#enable_or_disable.
    def visitEnable_or_disable(self, ctx:FirebirdParser.Enable_or_disableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#allow_or_disallow.
    def visitAllow_or_disallow(self, ctx:FirebirdParser.Allow_or_disallowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_synonym.
    def visitAlter_synonym(self, ctx:FirebirdParser.Alter_synonymContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_synonym.
    def visitCreate_synonym(self, ctx:FirebirdParser.Create_synonymContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_synonym.
    def visitDrop_synonym(self, ctx:FirebirdParser.Drop_synonymContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_spfile.
    def visitCreate_spfile(self, ctx:FirebirdParser.Create_spfileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#spfile_name.
    def visitSpfile_name(self, ctx:FirebirdParser.Spfile_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#pfile_name.
    def visitPfile_name(self, ctx:FirebirdParser.Pfile_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#comment_on_table.
    def visitComment_on_table(self, ctx:FirebirdParser.Comment_on_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#comment_on_materialized.
    def visitComment_on_materialized(self, ctx:FirebirdParser.Comment_on_materializedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_analytic_view.
    def visitAlter_analytic_view(self, ctx:FirebirdParser.Alter_analytic_viewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_add_cache_clause.
    def visitAlter_add_cache_clause(self, ctx:FirebirdParser.Alter_add_cache_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#levels_item.
    def visitLevels_item(self, ctx:FirebirdParser.Levels_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#measure_list.
    def visitMeasure_list(self, ctx:FirebirdParser.Measure_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_drop_cache_clause.
    def visitAlter_drop_cache_clause(self, ctx:FirebirdParser.Alter_drop_cache_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_attribute_dimension.
    def visitAlter_attribute_dimension(self, ctx:FirebirdParser.Alter_attribute_dimensionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_audit_policy.
    def visitAlter_audit_policy(self, ctx:FirebirdParser.Alter_audit_policyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_cluster.
    def visitAlter_cluster(self, ctx:FirebirdParser.Alter_clusterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_analytic_view.
    def visitDrop_analytic_view(self, ctx:FirebirdParser.Drop_analytic_viewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_attribute_dimension.
    def visitDrop_attribute_dimension(self, ctx:FirebirdParser.Drop_attribute_dimensionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_audit_policy.
    def visitDrop_audit_policy(self, ctx:FirebirdParser.Drop_audit_policyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_flashback_archive.
    def visitDrop_flashback_archive(self, ctx:FirebirdParser.Drop_flashback_archiveContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_cluster.
    def visitDrop_cluster(self, ctx:FirebirdParser.Drop_clusterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_context.
    def visitDrop_context(self, ctx:FirebirdParser.Drop_contextContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_directory.
    def visitDrop_directory(self, ctx:FirebirdParser.Drop_directoryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_diskgroup.
    def visitDrop_diskgroup(self, ctx:FirebirdParser.Drop_diskgroupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_edition.
    def visitDrop_edition(self, ctx:FirebirdParser.Drop_editionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#truncate_cluster.
    def visitTruncate_cluster(self, ctx:FirebirdParser.Truncate_clusterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#cache_or_nocache.
    def visitCache_or_nocache(self, ctx:FirebirdParser.Cache_or_nocacheContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#database_name.
    def visitDatabase_name(self, ctx:FirebirdParser.Database_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_database.
    def visitAlter_database(self, ctx:FirebirdParser.Alter_databaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#database_clause.
    def visitDatabase_clause(self, ctx:FirebirdParser.Database_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#startup_clauses.
    def visitStartup_clauses(self, ctx:FirebirdParser.Startup_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#resetlogs_or_noresetlogs.
    def visitResetlogs_or_noresetlogs(self, ctx:FirebirdParser.Resetlogs_or_noresetlogsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#upgrade_or_downgrade.
    def visitUpgrade_or_downgrade(self, ctx:FirebirdParser.Upgrade_or_downgradeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#recovery_clauses.
    def visitRecovery_clauses(self, ctx:FirebirdParser.Recovery_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#begin_or_end.
    def visitBegin_or_end(self, ctx:FirebirdParser.Begin_or_endContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#general_recovery.
    def visitGeneral_recovery(self, ctx:FirebirdParser.General_recoveryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#full_database_recovery.
    def visitFull_database_recovery(self, ctx:FirebirdParser.Full_database_recoveryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#partial_database_recovery.
    def visitPartial_database_recovery(self, ctx:FirebirdParser.Partial_database_recoveryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#partial_database_recovery_10g.
    def visitPartial_database_recovery_10g(self, ctx:FirebirdParser.Partial_database_recovery_10gContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#managed_standby_recovery.
    def visitManaged_standby_recovery(self, ctx:FirebirdParser.Managed_standby_recoveryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#db_name.
    def visitDb_name(self, ctx:FirebirdParser.Db_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#database_file_clauses.
    def visitDatabase_file_clauses(self, ctx:FirebirdParser.Database_file_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_datafile_clause.
    def visitCreate_datafile_clause(self, ctx:FirebirdParser.Create_datafile_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_datafile_clause.
    def visitAlter_datafile_clause(self, ctx:FirebirdParser.Alter_datafile_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_tempfile_clause.
    def visitAlter_tempfile_clause(self, ctx:FirebirdParser.Alter_tempfile_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#move_datafile_clause.
    def visitMove_datafile_clause(self, ctx:FirebirdParser.Move_datafile_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#logfile_clauses.
    def visitLogfile_clauses(self, ctx:FirebirdParser.Logfile_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#add_logfile_clauses.
    def visitAdd_logfile_clauses(self, ctx:FirebirdParser.Add_logfile_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#group_redo_logfile.
    def visitGroup_redo_logfile(self, ctx:FirebirdParser.Group_redo_logfileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_logfile_clauses.
    def visitDrop_logfile_clauses(self, ctx:FirebirdParser.Drop_logfile_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#switch_logfile_clause.
    def visitSwitch_logfile_clause(self, ctx:FirebirdParser.Switch_logfile_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#supplemental_db_logging.
    def visitSupplemental_db_logging(self, ctx:FirebirdParser.Supplemental_db_loggingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#add_or_drop.
    def visitAdd_or_drop(self, ctx:FirebirdParser.Add_or_dropContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#supplemental_plsql_clause.
    def visitSupplemental_plsql_clause(self, ctx:FirebirdParser.Supplemental_plsql_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#logfile_descriptor.
    def visitLogfile_descriptor(self, ctx:FirebirdParser.Logfile_descriptorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#controlfile_clauses.
    def visitControlfile_clauses(self, ctx:FirebirdParser.Controlfile_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#trace_file_clause.
    def visitTrace_file_clause(self, ctx:FirebirdParser.Trace_file_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#standby_database_clauses.
    def visitStandby_database_clauses(self, ctx:FirebirdParser.Standby_database_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#activate_standby_db_clause.
    def visitActivate_standby_db_clause(self, ctx:FirebirdParser.Activate_standby_db_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#maximize_standby_db_clause.
    def visitMaximize_standby_db_clause(self, ctx:FirebirdParser.Maximize_standby_db_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#register_logfile_clause.
    def visitRegister_logfile_clause(self, ctx:FirebirdParser.Register_logfile_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#commit_switchover_clause.
    def visitCommit_switchover_clause(self, ctx:FirebirdParser.Commit_switchover_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#start_standby_clause.
    def visitStart_standby_clause(self, ctx:FirebirdParser.Start_standby_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#stop_standby_clause.
    def visitStop_standby_clause(self, ctx:FirebirdParser.Stop_standby_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#convert_database_clause.
    def visitConvert_database_clause(self, ctx:FirebirdParser.Convert_database_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#default_settings_clause.
    def visitDefault_settings_clause(self, ctx:FirebirdParser.Default_settings_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#set_time_zone_clause.
    def visitSet_time_zone_clause(self, ctx:FirebirdParser.Set_time_zone_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#instance_clauses.
    def visitInstance_clauses(self, ctx:FirebirdParser.Instance_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#security_clause.
    def visitSecurity_clause(self, ctx:FirebirdParser.Security_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#domain.
    def visitDomain(self, ctx:FirebirdParser.DomainContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#database.
    def visitDatabase(self, ctx:FirebirdParser.DatabaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#edition_name.
    def visitEdition_name(self, ctx:FirebirdParser.Edition_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#filenumber.
    def visitFilenumber(self, ctx:FirebirdParser.FilenumberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#filename.
    def visitFilename(self, ctx:FirebirdParser.FilenameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#prepare_clause.
    def visitPrepare_clause(self, ctx:FirebirdParser.Prepare_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_mirror_clause.
    def visitDrop_mirror_clause(self, ctx:FirebirdParser.Drop_mirror_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lost_write_protection.
    def visitLost_write_protection(self, ctx:FirebirdParser.Lost_write_protectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#cdb_fleet_clauses.
    def visitCdb_fleet_clauses(self, ctx:FirebirdParser.Cdb_fleet_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lead_cdb_clause.
    def visitLead_cdb_clause(self, ctx:FirebirdParser.Lead_cdb_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lead_cdb_uri_clause.
    def visitLead_cdb_uri_clause(self, ctx:FirebirdParser.Lead_cdb_uri_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#property_clauses.
    def visitProperty_clauses(self, ctx:FirebirdParser.Property_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#replay_upgrade_clauses.
    def visitReplay_upgrade_clauses(self, ctx:FirebirdParser.Replay_upgrade_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_database_link.
    def visitAlter_database_link(self, ctx:FirebirdParser.Alter_database_linkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#password_value.
    def visitPassword_value(self, ctx:FirebirdParser.Password_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#link_authentication.
    def visitLink_authentication(self, ctx:FirebirdParser.Link_authenticationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_schema.
    def visitCreate_schema(self, ctx:FirebirdParser.Create_schemaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_database.
    def visitCreate_database(self, ctx:FirebirdParser.Create_databaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#database_logging_clauses.
    def visitDatabase_logging_clauses(self, ctx:FirebirdParser.Database_logging_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#database_logging_sub_clause.
    def visitDatabase_logging_sub_clause(self, ctx:FirebirdParser.Database_logging_sub_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#tablespace_clauses.
    def visitTablespace_clauses(self, ctx:FirebirdParser.Tablespace_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#enable_pluggable_database.
    def visitEnable_pluggable_database(self, ctx:FirebirdParser.Enable_pluggable_databaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#file_name_convert.
    def visitFile_name_convert(self, ctx:FirebirdParser.File_name_convertContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#filename_convert_sub_clause.
    def visitFilename_convert_sub_clause(self, ctx:FirebirdParser.Filename_convert_sub_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#tablespace_datafile_clauses.
    def visitTablespace_datafile_clauses(self, ctx:FirebirdParser.Tablespace_datafile_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#undo_mode_clause.
    def visitUndo_mode_clause(self, ctx:FirebirdParser.Undo_mode_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#default_tablespace.
    def visitDefault_tablespace(self, ctx:FirebirdParser.Default_tablespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#default_temp_tablespace.
    def visitDefault_temp_tablespace(self, ctx:FirebirdParser.Default_temp_tablespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#undo_tablespace.
    def visitUndo_tablespace(self, ctx:FirebirdParser.Undo_tablespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_database.
    def visitDrop_database(self, ctx:FirebirdParser.Drop_databaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#create_database_link.
    def visitCreate_database_link(self, ctx:FirebirdParser.Create_database_linkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_database_link.
    def visitDrop_database_link(self, ctx:FirebirdParser.Drop_database_linkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_tablespace_set.
    def visitAlter_tablespace_set(self, ctx:FirebirdParser.Alter_tablespace_setContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_tablespace_attrs.
    def visitAlter_tablespace_attrs(self, ctx:FirebirdParser.Alter_tablespace_attrsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_tablespace_encryption.
    def visitAlter_tablespace_encryption(self, ctx:FirebirdParser.Alter_tablespace_encryptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#ts_file_name_convert.
    def visitTs_file_name_convert(self, ctx:FirebirdParser.Ts_file_name_convertContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_role.
    def visitAlter_role(self, ctx:FirebirdParser.Alter_roleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#role_identified_clause.
    def visitRole_identified_clause(self, ctx:FirebirdParser.Role_identified_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_table.
    def visitAlter_table(self, ctx:FirebirdParser.Alter_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#memoptimize_read_write_clause.
    def visitMemoptimize_read_write_clause(self, ctx:FirebirdParser.Memoptimize_read_write_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_table_properties.
    def visitAlter_table_properties(self, ctx:FirebirdParser.Alter_table_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_table_partitioning.
    def visitAlter_table_partitioning(self, ctx:FirebirdParser.Alter_table_partitioningContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#add_table_partition.
    def visitAdd_table_partition(self, ctx:FirebirdParser.Add_table_partitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_table_partition.
    def visitDrop_table_partition(self, ctx:FirebirdParser.Drop_table_partitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#merge_table_partition.
    def visitMerge_table_partition(self, ctx:FirebirdParser.Merge_table_partitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#modify_table_partition.
    def visitModify_table_partition(self, ctx:FirebirdParser.Modify_table_partitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#split_table_partition.
    def visitSplit_table_partition(self, ctx:FirebirdParser.Split_table_partitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#truncate_table_partition.
    def visitTruncate_table_partition(self, ctx:FirebirdParser.Truncate_table_partitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#exchange_table_partition.
    def visitExchange_table_partition(self, ctx:FirebirdParser.Exchange_table_partitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#coalesce_table_partition.
    def visitCoalesce_table_partition(self, ctx:FirebirdParser.Coalesce_table_partitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_interval_partition.
    def visitAlter_interval_partition(self, ctx:FirebirdParser.Alter_interval_partitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#move_table_partition.
    def visitMove_table_partition(self, ctx:FirebirdParser.Move_table_partitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#filter_condition.
    def visitFilter_condition(self, ctx:FirebirdParser.Filter_conditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#rename_table_partition.
    def visitRename_table_partition(self, ctx:FirebirdParser.Rename_table_partitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#partition_extended_names.
    def visitPartition_extended_names(self, ctx:FirebirdParser.Partition_extended_namesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#subpartition_extended_names.
    def visitSubpartition_extended_names(self, ctx:FirebirdParser.Subpartition_extended_namesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_table_properties_1.
    def visitAlter_table_properties_1(self, ctx:FirebirdParser.Alter_table_properties_1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_iot_clauses.
    def visitAlter_iot_clauses(self, ctx:FirebirdParser.Alter_iot_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_mapping_table_clause.
    def visitAlter_mapping_table_clause(self, ctx:FirebirdParser.Alter_mapping_table_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#alter_overflow_clause.
    def visitAlter_overflow_clause(self, ctx:FirebirdParser.Alter_overflow_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#add_overflow_clause.
    def visitAdd_overflow_clause(self, ctx:FirebirdParser.Add_overflow_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#update_index_clauses.
    def visitUpdate_index_clauses(self, ctx:FirebirdParser.Update_index_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#update_global_index_clause.
    def visitUpdate_global_index_clause(self, ctx:FirebirdParser.Update_global_index_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#update_all_indexes_clause.
    def visitUpdate_all_indexes_clause(self, ctx:FirebirdParser.Update_all_indexes_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#update_all_indexes_index_clause.
    def visitUpdate_all_indexes_index_clause(self, ctx:FirebirdParser.Update_all_indexes_index_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#update_index_partition.
    def visitUpdate_index_partition(self, ctx:FirebirdParser.Update_index_partitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#update_index_subpartition.
    def visitUpdate_index_subpartition(self, ctx:FirebirdParser.Update_index_subpartitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#enable_disable_clause.
    def visitEnable_disable_clause(self, ctx:FirebirdParser.Enable_disable_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#using_index_clause.
    def visitUsing_index_clause(self, ctx:FirebirdParser.Using_index_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#index_attributes.
    def visitIndex_attributes(self, ctx:FirebirdParser.Index_attributesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#sort_or_nosort.
    def visitSort_or_nosort(self, ctx:FirebirdParser.Sort_or_nosortContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#exceptions_clause.
    def visitExceptions_clause(self, ctx:FirebirdParser.Exceptions_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#move_table_clause.
    def visitMove_table_clause(self, ctx:FirebirdParser.Move_table_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#index_org_table_clause.
    def visitIndex_org_table_clause(self, ctx:FirebirdParser.Index_org_table_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#mapping_table_clause.
    def visitMapping_table_clause(self, ctx:FirebirdParser.Mapping_table_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#key_compression.
    def visitKey_compression(self, ctx:FirebirdParser.Key_compressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#index_org_overflow_clause.
    def visitIndex_org_overflow_clause(self, ctx:FirebirdParser.Index_org_overflow_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#column_clauses.
    def visitColumn_clauses(self, ctx:FirebirdParser.Column_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#modify_collection_retrieval.
    def visitModify_collection_retrieval(self, ctx:FirebirdParser.Modify_collection_retrievalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#collection_item.
    def visitCollection_item(self, ctx:FirebirdParser.Collection_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#rename_column_clause.
    def visitRename_column_clause(self, ctx:FirebirdParser.Rename_column_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#old_column_name.
    def visitOld_column_name(self, ctx:FirebirdParser.Old_column_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#new_column_name.
    def visitNew_column_name(self, ctx:FirebirdParser.New_column_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#add_modify_drop_column_clauses.
    def visitAdd_modify_drop_column_clauses(self, ctx:FirebirdParser.Add_modify_drop_column_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_column_clause.
    def visitDrop_column_clause(self, ctx:FirebirdParser.Drop_column_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#modify_column_clauses.
    def visitModify_column_clauses(self, ctx:FirebirdParser.Modify_column_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#modify_col_properties.
    def visitModify_col_properties(self, ctx:FirebirdParser.Modify_col_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#modify_col_visibility.
    def visitModify_col_visibility(self, ctx:FirebirdParser.Modify_col_visibilityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#modify_col_substitutable.
    def visitModify_col_substitutable(self, ctx:FirebirdParser.Modify_col_substitutableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#add_column_clause.
    def visitAdd_column_clause(self, ctx:FirebirdParser.Add_column_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#varray_col_properties.
    def visitVarray_col_properties(self, ctx:FirebirdParser.Varray_col_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#varray_storage_clause.
    def visitVarray_storage_clause(self, ctx:FirebirdParser.Varray_storage_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lob_segname.
    def visitLob_segname(self, ctx:FirebirdParser.Lob_segnameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lob_item.
    def visitLob_item(self, ctx:FirebirdParser.Lob_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lob_storage_parameters.
    def visitLob_storage_parameters(self, ctx:FirebirdParser.Lob_storage_parametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lob_storage_clause.
    def visitLob_storage_clause(self, ctx:FirebirdParser.Lob_storage_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#modify_lob_storage_clause.
    def visitModify_lob_storage_clause(self, ctx:FirebirdParser.Modify_lob_storage_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#modify_lob_parameters.
    def visitModify_lob_parameters(self, ctx:FirebirdParser.Modify_lob_parametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lob_parameters.
    def visitLob_parameters(self, ctx:FirebirdParser.Lob_parametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lob_deduplicate_clause.
    def visitLob_deduplicate_clause(self, ctx:FirebirdParser.Lob_deduplicate_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lob_compression_clause.
    def visitLob_compression_clause(self, ctx:FirebirdParser.Lob_compression_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lob_retention_clause.
    def visitLob_retention_clause(self, ctx:FirebirdParser.Lob_retention_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#encryption_spec.
    def visitEncryption_spec(self, ctx:FirebirdParser.Encryption_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#tablespace.
    def visitTablespace(self, ctx:FirebirdParser.TablespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#varray_item.
    def visitVarray_item(self, ctx:FirebirdParser.Varray_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#column_properties.
    def visitColumn_properties(self, ctx:FirebirdParser.Column_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lob_partition_storage.
    def visitLob_partition_storage(self, ctx:FirebirdParser.Lob_partition_storageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#period_definition.
    def visitPeriod_definition(self, ctx:FirebirdParser.Period_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#start_time_column.
    def visitStart_time_column(self, ctx:FirebirdParser.Start_time_columnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#end_time_column.
    def visitEnd_time_column(self, ctx:FirebirdParser.End_time_columnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#column_definition.
    def visitColumn_definition(self, ctx:FirebirdParser.Column_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#column_collation_name.
    def visitColumn_collation_name(self, ctx:FirebirdParser.Column_collation_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#identity_clause.
    def visitIdentity_clause(self, ctx:FirebirdParser.Identity_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#identity_options_parentheses.
    def visitIdentity_options_parentheses(self, ctx:FirebirdParser.Identity_options_parenthesesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#identity_options.
    def visitIdentity_options(self, ctx:FirebirdParser.Identity_optionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#virtual_column_definition.
    def visitVirtual_column_definition(self, ctx:FirebirdParser.Virtual_column_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#virtual_column_expression.
    def visitVirtual_column_expression(self, ctx:FirebirdParser.Virtual_column_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#autogenerated_sequence_definition.
    def visitAutogenerated_sequence_definition(self, ctx:FirebirdParser.Autogenerated_sequence_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#by_user_for_statistics_clause.
    def visitBy_user_for_statistics_clause(self, ctx:FirebirdParser.By_user_for_statistics_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#evaluation_edition_clause.
    def visitEvaluation_edition_clause(self, ctx:FirebirdParser.Evaluation_edition_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#nested_table_col_properties.
    def visitNested_table_col_properties(self, ctx:FirebirdParser.Nested_table_col_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#nested_item.
    def visitNested_item(self, ctx:FirebirdParser.Nested_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#substitutable_column_clause.
    def visitSubstitutable_column_clause(self, ctx:FirebirdParser.Substitutable_column_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#partition_name.
    def visitPartition_name(self, ctx:FirebirdParser.Partition_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#supplemental_logging_props.
    def visitSupplemental_logging_props(self, ctx:FirebirdParser.Supplemental_logging_propsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#object_type_col_properties.
    def visitObject_type_col_properties(self, ctx:FirebirdParser.Object_type_col_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#constraint_clauses.
    def visitConstraint_clauses(self, ctx:FirebirdParser.Constraint_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#old_constraint_name.
    def visitOld_constraint_name(self, ctx:FirebirdParser.Old_constraint_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#new_constraint_name.
    def visitNew_constraint_name(self, ctx:FirebirdParser.New_constraint_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#drop_constraint_clause.
    def visitDrop_constraint_clause(self, ctx:FirebirdParser.Drop_constraint_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#check_constraint.
    def visitCheck_constraint(self, ctx:FirebirdParser.Check_constraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#foreign_key_clause.
    def visitForeign_key_clause(self, ctx:FirebirdParser.Foreign_key_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#references_clause.
    def visitReferences_clause(self, ctx:FirebirdParser.References_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#on_delete_clause.
    def visitOn_delete_clause(self, ctx:FirebirdParser.On_delete_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#anonymous_block.
    def visitAnonymous_block(self, ctx:FirebirdParser.Anonymous_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#invoker_rights_clause.
    def visitInvoker_rights_clause(self, ctx:FirebirdParser.Invoker_rights_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#call_spec.
    def visitCall_spec(self, ctx:FirebirdParser.Call_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#java_spec.
    def visitJava_spec(self, ctx:FirebirdParser.Java_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#c_spec.
    def visitC_spec(self, ctx:FirebirdParser.C_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#c_agent_in_clause.
    def visitC_agent_in_clause(self, ctx:FirebirdParser.C_agent_in_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#c_parameters_clause.
    def visitC_parameters_clause(self, ctx:FirebirdParser.C_parameters_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#c_external_parameter.
    def visitC_external_parameter(self, ctx:FirebirdParser.C_external_parameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#c_property.
    def visitC_property(self, ctx:FirebirdParser.C_propertyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#parameter.
    def visitParameter(self, ctx:FirebirdParser.ParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#default_value_part.
    def visitDefault_value_part(self, ctx:FirebirdParser.Default_value_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#seq_of_declare_specs.
    def visitSeq_of_declare_specs(self, ctx:FirebirdParser.Seq_of_declare_specsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#declare_spec.
    def visitDeclare_spec(self, ctx:FirebirdParser.Declare_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#variable_declaration.
    def visitVariable_declaration(self, ctx:FirebirdParser.Variable_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#subtype_declaration.
    def visitSubtype_declaration(self, ctx:FirebirdParser.Subtype_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#cursor_declaration.
    def visitCursor_declaration(self, ctx:FirebirdParser.Cursor_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#parameter_spec.
    def visitParameter_spec(self, ctx:FirebirdParser.Parameter_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#exception_declaration.
    def visitException_declaration(self, ctx:FirebirdParser.Exception_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#pragma_declaration.
    def visitPragma_declaration(self, ctx:FirebirdParser.Pragma_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#record_type_def.
    def visitRecord_type_def(self, ctx:FirebirdParser.Record_type_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#field_spec.
    def visitField_spec(self, ctx:FirebirdParser.Field_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#ref_cursor_type_def.
    def visitRef_cursor_type_def(self, ctx:FirebirdParser.Ref_cursor_type_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#type_declaration.
    def visitType_declaration(self, ctx:FirebirdParser.Type_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#table_type_def.
    def visitTable_type_def(self, ctx:FirebirdParser.Table_type_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#table_indexed_by_part.
    def visitTable_indexed_by_part(self, ctx:FirebirdParser.Table_indexed_by_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#varray_type_def.
    def visitVarray_type_def(self, ctx:FirebirdParser.Varray_type_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#seq_of_statements.
    def visitSeq_of_statements(self, ctx:FirebirdParser.Seq_of_statementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#label_declaration.
    def visitLabel_declaration(self, ctx:FirebirdParser.Label_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#statement.
    def visitStatement(self, ctx:FirebirdParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#assignment_statement.
    def visitAssignment_statement(self, ctx:FirebirdParser.Assignment_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#continue_statement.
    def visitContinue_statement(self, ctx:FirebirdParser.Continue_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#exit_statement.
    def visitExit_statement(self, ctx:FirebirdParser.Exit_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#goto_statement.
    def visitGoto_statement(self, ctx:FirebirdParser.Goto_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#if_statement.
    def visitIf_statement(self, ctx:FirebirdParser.If_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#elsif_part.
    def visitElsif_part(self, ctx:FirebirdParser.Elsif_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#else_part.
    def visitElse_part(self, ctx:FirebirdParser.Else_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#loop_statement.
    def visitLoop_statement(self, ctx:FirebirdParser.Loop_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#cursor_loop_param.
    def visitCursor_loop_param(self, ctx:FirebirdParser.Cursor_loop_paramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#forall_statement.
    def visitForall_statement(self, ctx:FirebirdParser.Forall_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#bounds_clause.
    def visitBounds_clause(self, ctx:FirebirdParser.Bounds_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#between_bound.
    def visitBetween_bound(self, ctx:FirebirdParser.Between_boundContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lower_bound.
    def visitLower_bound(self, ctx:FirebirdParser.Lower_boundContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#upper_bound.
    def visitUpper_bound(self, ctx:FirebirdParser.Upper_boundContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#null_statement.
    def visitNull_statement(self, ctx:FirebirdParser.Null_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#raise_statement.
    def visitRaise_statement(self, ctx:FirebirdParser.Raise_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#return_statement.
    def visitReturn_statement(self, ctx:FirebirdParser.Return_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#call_statement.
    def visitCall_statement(self, ctx:FirebirdParser.Call_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#pipe_row_statement.
    def visitPipe_row_statement(self, ctx:FirebirdParser.Pipe_row_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#selection_directive.
    def visitSelection_directive(self, ctx:FirebirdParser.Selection_directiveContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#error_directive.
    def visitError_directive(self, ctx:FirebirdParser.Error_directiveContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#selection_directive_body.
    def visitSelection_directive_body(self, ctx:FirebirdParser.Selection_directive_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#body.
    def visitBody(self, ctx:FirebirdParser.BodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#exception_handler.
    def visitException_handler(self, ctx:FirebirdParser.Exception_handlerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#trigger_block.
    def visitTrigger_block(self, ctx:FirebirdParser.Trigger_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#tps_block.
    def visitTps_block(self, ctx:FirebirdParser.Tps_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#block.
    def visitBlock(self, ctx:FirebirdParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#sql_statement.
    def visitSql_statement(self, ctx:FirebirdParser.Sql_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#execute_statement.
    def visitExecute_statement(self, ctx:FirebirdParser.Execute_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#dynamic_returning_clause.
    def visitDynamic_returning_clause(self, ctx:FirebirdParser.Dynamic_returning_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#data_manipulation_language_statements.
    def visitData_manipulation_language_statements(self, ctx:FirebirdParser.Data_manipulation_language_statementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#cursor_manipulation_statements.
    def visitCursor_manipulation_statements(self, ctx:FirebirdParser.Cursor_manipulation_statementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#close_statement.
    def visitClose_statement(self, ctx:FirebirdParser.Close_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#open_statement.
    def visitOpen_statement(self, ctx:FirebirdParser.Open_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#fetch_statement.
    def visitFetch_statement(self, ctx:FirebirdParser.Fetch_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#variable_or_collection.
    def visitVariable_or_collection(self, ctx:FirebirdParser.Variable_or_collectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#open_for_statement.
    def visitOpen_for_statement(self, ctx:FirebirdParser.Open_for_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#transaction_control_statements.
    def visitTransaction_control_statements(self, ctx:FirebirdParser.Transaction_control_statementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#set_transaction_command.
    def visitSet_transaction_command(self, ctx:FirebirdParser.Set_transaction_commandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#set_constraint_command.
    def visitSet_constraint_command(self, ctx:FirebirdParser.Set_constraint_commandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#commit_statement.
    def visitCommit_statement(self, ctx:FirebirdParser.Commit_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#write_clause.
    def visitWrite_clause(self, ctx:FirebirdParser.Write_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#rollback_statement.
    def visitRollback_statement(self, ctx:FirebirdParser.Rollback_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#savepoint_statement.
    def visitSavepoint_statement(self, ctx:FirebirdParser.Savepoint_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#collection_method_call.
    def visitCollection_method_call(self, ctx:FirebirdParser.Collection_method_callContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#explain_statement.
    def visitExplain_statement(self, ctx:FirebirdParser.Explain_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#select_only_statement.
    def visitSelect_only_statement(self, ctx:FirebirdParser.Select_only_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#select_statement.
    def visitSelect_statement(self, ctx:FirebirdParser.Select_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#with_clause.
    def visitWith_clause(self, ctx:FirebirdParser.With_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#with_factoring_clause.
    def visitWith_factoring_clause(self, ctx:FirebirdParser.With_factoring_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#subquery_factoring_clause.
    def visitSubquery_factoring_clause(self, ctx:FirebirdParser.Subquery_factoring_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#search_clause.
    def visitSearch_clause(self, ctx:FirebirdParser.Search_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#cycle_clause.
    def visitCycle_clause(self, ctx:FirebirdParser.Cycle_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#subav_factoring_clause.
    def visitSubav_factoring_clause(self, ctx:FirebirdParser.Subav_factoring_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#subav_clause.
    def visitSubav_clause(self, ctx:FirebirdParser.Subav_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#hierarchies_clause.
    def visitHierarchies_clause(self, ctx:FirebirdParser.Hierarchies_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#filter_clauses.
    def visitFilter_clauses(self, ctx:FirebirdParser.Filter_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#filter_clause.
    def visitFilter_clause(self, ctx:FirebirdParser.Filter_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#add_calcs_clause.
    def visitAdd_calcs_clause(self, ctx:FirebirdParser.Add_calcs_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#add_calc_meas_clause.
    def visitAdd_calc_meas_clause(self, ctx:FirebirdParser.Add_calc_meas_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#subquery.
    def visitSubquery(self, ctx:FirebirdParser.SubqueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#subquery_basic_elements.
    def visitSubquery_basic_elements(self, ctx:FirebirdParser.Subquery_basic_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#subquery_operation_part.
    def visitSubquery_operation_part(self, ctx:FirebirdParser.Subquery_operation_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#query_block.
    def visitQuery_block(self, ctx:FirebirdParser.Query_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#selected_list.
    def visitSelected_list(self, ctx:FirebirdParser.Selected_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#from_clause.
    def visitFrom_clause(self, ctx:FirebirdParser.From_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#select_list_elements.
    def visitSelect_list_elements(self, ctx:FirebirdParser.Select_list_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#table_ref_list.
    def visitTable_ref_list(self, ctx:FirebirdParser.Table_ref_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#table_ref.
    def visitTable_ref(self, ctx:FirebirdParser.Table_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#table_ref_aux.
    def visitTable_ref_aux(self, ctx:FirebirdParser.Table_ref_auxContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#table_ref_aux_internal_one.
    def visitTable_ref_aux_internal_one(self, ctx:FirebirdParser.Table_ref_aux_internal_oneContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#table_ref_aux_internal_two.
    def visitTable_ref_aux_internal_two(self, ctx:FirebirdParser.Table_ref_aux_internal_twoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#table_ref_aux_internal_thre.
    def visitTable_ref_aux_internal_thre(self, ctx:FirebirdParser.Table_ref_aux_internal_threContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#join_clause.
    def visitJoin_clause(self, ctx:FirebirdParser.Join_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#join_on_part.
    def visitJoin_on_part(self, ctx:FirebirdParser.Join_on_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#join_using_part.
    def visitJoin_using_part(self, ctx:FirebirdParser.Join_using_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#outer_join_type.
    def visitOuter_join_type(self, ctx:FirebirdParser.Outer_join_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#query_partition_clause.
    def visitQuery_partition_clause(self, ctx:FirebirdParser.Query_partition_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#flashback_query_clause.
    def visitFlashback_query_clause(self, ctx:FirebirdParser.Flashback_query_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#pivot_clause.
    def visitPivot_clause(self, ctx:FirebirdParser.Pivot_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#pivot_element.
    def visitPivot_element(self, ctx:FirebirdParser.Pivot_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#pivot_for_clause.
    def visitPivot_for_clause(self, ctx:FirebirdParser.Pivot_for_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#pivot_in_clause.
    def visitPivot_in_clause(self, ctx:FirebirdParser.Pivot_in_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#pivot_in_clause_element.
    def visitPivot_in_clause_element(self, ctx:FirebirdParser.Pivot_in_clause_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#pivot_in_clause_elements.
    def visitPivot_in_clause_elements(self, ctx:FirebirdParser.Pivot_in_clause_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#unpivot_clause.
    def visitUnpivot_clause(self, ctx:FirebirdParser.Unpivot_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#unpivot_in_clause.
    def visitUnpivot_in_clause(self, ctx:FirebirdParser.Unpivot_in_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#unpivot_in_elements.
    def visitUnpivot_in_elements(self, ctx:FirebirdParser.Unpivot_in_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#hierarchical_query_clause.
    def visitHierarchical_query_clause(self, ctx:FirebirdParser.Hierarchical_query_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#start_part.
    def visitStart_part(self, ctx:FirebirdParser.Start_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#group_by_clause.
    def visitGroup_by_clause(self, ctx:FirebirdParser.Group_by_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#group_by_elements.
    def visitGroup_by_elements(self, ctx:FirebirdParser.Group_by_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#rollup_cube_clause.
    def visitRollup_cube_clause(self, ctx:FirebirdParser.Rollup_cube_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#grouping_sets_clause.
    def visitGrouping_sets_clause(self, ctx:FirebirdParser.Grouping_sets_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#grouping_sets_elements.
    def visitGrouping_sets_elements(self, ctx:FirebirdParser.Grouping_sets_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#having_clause.
    def visitHaving_clause(self, ctx:FirebirdParser.Having_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#model_clause.
    def visitModel_clause(self, ctx:FirebirdParser.Model_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#cell_reference_options.
    def visitCell_reference_options(self, ctx:FirebirdParser.Cell_reference_optionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#return_rows_clause.
    def visitReturn_rows_clause(self, ctx:FirebirdParser.Return_rows_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#reference_model.
    def visitReference_model(self, ctx:FirebirdParser.Reference_modelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#main_model.
    def visitMain_model(self, ctx:FirebirdParser.Main_modelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#model_column_clauses.
    def visitModel_column_clauses(self, ctx:FirebirdParser.Model_column_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#model_column_partition_part.
    def visitModel_column_partition_part(self, ctx:FirebirdParser.Model_column_partition_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#model_column_list.
    def visitModel_column_list(self, ctx:FirebirdParser.Model_column_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#model_column.
    def visitModel_column(self, ctx:FirebirdParser.Model_columnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#model_rules_clause.
    def visitModel_rules_clause(self, ctx:FirebirdParser.Model_rules_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#model_rules_part.
    def visitModel_rules_part(self, ctx:FirebirdParser.Model_rules_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#model_rules_element.
    def visitModel_rules_element(self, ctx:FirebirdParser.Model_rules_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#cell_assignment.
    def visitCell_assignment(self, ctx:FirebirdParser.Cell_assignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#model_iterate_clause.
    def visitModel_iterate_clause(self, ctx:FirebirdParser.Model_iterate_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#until_part.
    def visitUntil_part(self, ctx:FirebirdParser.Until_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#order_by_clause.
    def visitOrder_by_clause(self, ctx:FirebirdParser.Order_by_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#order_by_elements.
    def visitOrder_by_elements(self, ctx:FirebirdParser.Order_by_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#offset_clause.
    def visitOffset_clause(self, ctx:FirebirdParser.Offset_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#fetch_clause.
    def visitFetch_clause(self, ctx:FirebirdParser.Fetch_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#for_update_clause.
    def visitFor_update_clause(self, ctx:FirebirdParser.For_update_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#for_update_of_part.
    def visitFor_update_of_part(self, ctx:FirebirdParser.For_update_of_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#for_update_options.
    def visitFor_update_options(self, ctx:FirebirdParser.For_update_optionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#update_statement.
    def visitUpdate_statement(self, ctx:FirebirdParser.Update_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#update_set_clause.
    def visitUpdate_set_clause(self, ctx:FirebirdParser.Update_set_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#column_based_update_set_clause.
    def visitColumn_based_update_set_clause(self, ctx:FirebirdParser.Column_based_update_set_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#delete_statement.
    def visitDelete_statement(self, ctx:FirebirdParser.Delete_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#insert_statement.
    def visitInsert_statement(self, ctx:FirebirdParser.Insert_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#single_table_insert.
    def visitSingle_table_insert(self, ctx:FirebirdParser.Single_table_insertContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#multi_table_insert.
    def visitMulti_table_insert(self, ctx:FirebirdParser.Multi_table_insertContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#multi_table_element.
    def visitMulti_table_element(self, ctx:FirebirdParser.Multi_table_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#conditional_insert_clause.
    def visitConditional_insert_clause(self, ctx:FirebirdParser.Conditional_insert_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#conditional_insert_when_part.
    def visitConditional_insert_when_part(self, ctx:FirebirdParser.Conditional_insert_when_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#conditional_insert_else_part.
    def visitConditional_insert_else_part(self, ctx:FirebirdParser.Conditional_insert_else_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#insert_into_clause.
    def visitInsert_into_clause(self, ctx:FirebirdParser.Insert_into_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#values_clause.
    def visitValues_clause(self, ctx:FirebirdParser.Values_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#merge_statement.
    def visitMerge_statement(self, ctx:FirebirdParser.Merge_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#merge_update_clause.
    def visitMerge_update_clause(self, ctx:FirebirdParser.Merge_update_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#merge_element.
    def visitMerge_element(self, ctx:FirebirdParser.Merge_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#merge_update_delete_part.
    def visitMerge_update_delete_part(self, ctx:FirebirdParser.Merge_update_delete_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#merge_insert_clause.
    def visitMerge_insert_clause(self, ctx:FirebirdParser.Merge_insert_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#selected_tableview.
    def visitSelected_tableview(self, ctx:FirebirdParser.Selected_tableviewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lock_table_statement.
    def visitLock_table_statement(self, ctx:FirebirdParser.Lock_table_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#wait_nowait_part.
    def visitWait_nowait_part(self, ctx:FirebirdParser.Wait_nowait_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lock_table_element.
    def visitLock_table_element(self, ctx:FirebirdParser.Lock_table_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#lock_mode.
    def visitLock_mode(self, ctx:FirebirdParser.Lock_modeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#general_table_ref.
    def visitGeneral_table_ref(self, ctx:FirebirdParser.General_table_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#static_returning_clause.
    def visitStatic_returning_clause(self, ctx:FirebirdParser.Static_returning_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#error_logging_clause.
    def visitError_logging_clause(self, ctx:FirebirdParser.Error_logging_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#error_logging_into_part.
    def visitError_logging_into_part(self, ctx:FirebirdParser.Error_logging_into_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#error_logging_reject_part.
    def visitError_logging_reject_part(self, ctx:FirebirdParser.Error_logging_reject_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#dml_table_expression_clause.
    def visitDml_table_expression_clause(self, ctx:FirebirdParser.Dml_table_expression_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#table_collection_expression.
    def visitTable_collection_expression(self, ctx:FirebirdParser.Table_collection_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#subquery_restriction_clause.
    def visitSubquery_restriction_clause(self, ctx:FirebirdParser.Subquery_restriction_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#sample_clause.
    def visitSample_clause(self, ctx:FirebirdParser.Sample_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#seed_part.
    def visitSeed_part(self, ctx:FirebirdParser.Seed_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#condition.
    def visitCondition(self, ctx:FirebirdParser.ConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#expressions_.
    def visitExpressions_(self, ctx:FirebirdParser.Expressions_Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#expression.
    def visitExpression(self, ctx:FirebirdParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#cursor_expression.
    def visitCursor_expression(self, ctx:FirebirdParser.Cursor_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#logical_expression.
    def visitLogical_expression(self, ctx:FirebirdParser.Logical_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#unary_logical_expression.
    def visitUnary_logical_expression(self, ctx:FirebirdParser.Unary_logical_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#unary_logical_operation.
    def visitUnary_logical_operation(self, ctx:FirebirdParser.Unary_logical_operationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#logical_operation.
    def visitLogical_operation(self, ctx:FirebirdParser.Logical_operationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#multiset_expression.
    def visitMultiset_expression(self, ctx:FirebirdParser.Multiset_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#relational_expression.
    def visitRelational_expression(self, ctx:FirebirdParser.Relational_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#compound_expression.
    def visitCompound_expression(self, ctx:FirebirdParser.Compound_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#relational_operator.
    def visitRelational_operator(self, ctx:FirebirdParser.Relational_operatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#in_elements.
    def visitIn_elements(self, ctx:FirebirdParser.In_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#between_elements.
    def visitBetween_elements(self, ctx:FirebirdParser.Between_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#concatenation.
    def visitConcatenation(self, ctx:FirebirdParser.ConcatenationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#interval_expression.
    def visitInterval_expression(self, ctx:FirebirdParser.Interval_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#model_expression.
    def visitModel_expression(self, ctx:FirebirdParser.Model_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#model_expression_element.
    def visitModel_expression_element(self, ctx:FirebirdParser.Model_expression_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#single_column_for_loop.
    def visitSingle_column_for_loop(self, ctx:FirebirdParser.Single_column_for_loopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#multi_column_for_loop.
    def visitMulti_column_for_loop(self, ctx:FirebirdParser.Multi_column_for_loopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#unary_expression.
    def visitUnary_expression(self, ctx:FirebirdParser.Unary_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#unary_expression_core.
    def visitUnary_expression_core(self, ctx:FirebirdParser.Unary_expression_coreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#implicit_cursor_expression.
    def visitImplicit_cursor_expression(self, ctx:FirebirdParser.Implicit_cursor_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#collection_expression.
    def visitCollection_expression(self, ctx:FirebirdParser.Collection_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#case_statement.
    def visitCase_statement(self, ctx:FirebirdParser.Case_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#simple_case_statement.
    def visitSimple_case_statement(self, ctx:FirebirdParser.Simple_case_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#searched_case_statement.
    def visitSearched_case_statement(self, ctx:FirebirdParser.Searched_case_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#case_when_part_statement.
    def visitCase_when_part_statement(self, ctx:FirebirdParser.Case_when_part_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#case_else_part_statement.
    def visitCase_else_part_statement(self, ctx:FirebirdParser.Case_else_part_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#case_expression.
    def visitCase_expression(self, ctx:FirebirdParser.Case_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#simple_case_expression.
    def visitSimple_case_expression(self, ctx:FirebirdParser.Simple_case_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#searched_case_expression.
    def visitSearched_case_expression(self, ctx:FirebirdParser.Searched_case_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#case_when_part_expression.
    def visitCase_when_part_expression(self, ctx:FirebirdParser.Case_when_part_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#case_else_part_expression.
    def visitCase_else_part_expression(self, ctx:FirebirdParser.Case_else_part_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#atom.
    def visitAtom(self, ctx:FirebirdParser.AtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#quantified_expression.
    def visitQuantified_expression(self, ctx:FirebirdParser.Quantified_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#string_function.
    def visitString_function(self, ctx:FirebirdParser.String_functionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#standard_function.
    def visitStandard_function(self, ctx:FirebirdParser.Standard_functionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#json_function.
    def visitJson_function(self, ctx:FirebirdParser.Json_functionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#json_object_content.
    def visitJson_object_content(self, ctx:FirebirdParser.Json_object_contentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#json_object_entry.
    def visitJson_object_entry(self, ctx:FirebirdParser.Json_object_entryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#json_table_clause.
    def visitJson_table_clause(self, ctx:FirebirdParser.Json_table_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#json_array_element.
    def visitJson_array_element(self, ctx:FirebirdParser.Json_array_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#json_on_null_clause.
    def visitJson_on_null_clause(self, ctx:FirebirdParser.Json_on_null_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#json_return_clause.
    def visitJson_return_clause(self, ctx:FirebirdParser.Json_return_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#json_transform_op.
    def visitJson_transform_op(self, ctx:FirebirdParser.Json_transform_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#json_column_clause.
    def visitJson_column_clause(self, ctx:FirebirdParser.Json_column_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#json_column_definition.
    def visitJson_column_definition(self, ctx:FirebirdParser.Json_column_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#json_query_returning_clause.
    def visitJson_query_returning_clause(self, ctx:FirebirdParser.Json_query_returning_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#json_query_return_type.
    def visitJson_query_return_type(self, ctx:FirebirdParser.Json_query_return_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#json_query_wrapper_clause.
    def visitJson_query_wrapper_clause(self, ctx:FirebirdParser.Json_query_wrapper_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#json_query_on_error_clause.
    def visitJson_query_on_error_clause(self, ctx:FirebirdParser.Json_query_on_error_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#json_query_on_empty_clause.
    def visitJson_query_on_empty_clause(self, ctx:FirebirdParser.Json_query_on_empty_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#json_value_return_clause.
    def visitJson_value_return_clause(self, ctx:FirebirdParser.Json_value_return_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#json_value_return_type.
    def visitJson_value_return_type(self, ctx:FirebirdParser.Json_value_return_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#json_value_on_mismatch_clause.
    def visitJson_value_on_mismatch_clause(self, ctx:FirebirdParser.Json_value_on_mismatch_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#literal.
    def visitLiteral(self, ctx:FirebirdParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#numeric_function_wrapper.
    def visitNumeric_function_wrapper(self, ctx:FirebirdParser.Numeric_function_wrapperContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#numeric_function.
    def visitNumeric_function(self, ctx:FirebirdParser.Numeric_functionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#listagg_overflow_clause.
    def visitListagg_overflow_clause(self, ctx:FirebirdParser.Listagg_overflow_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#other_function.
    def visitOther_function(self, ctx:FirebirdParser.Other_functionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#over_clause_keyword.
    def visitOver_clause_keyword(self, ctx:FirebirdParser.Over_clause_keywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#within_or_over_clause_keyword.
    def visitWithin_or_over_clause_keyword(self, ctx:FirebirdParser.Within_or_over_clause_keywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#standard_prediction_function_keyword.
    def visitStandard_prediction_function_keyword(self, ctx:FirebirdParser.Standard_prediction_function_keywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#over_clause.
    def visitOver_clause(self, ctx:FirebirdParser.Over_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#windowing_clause.
    def visitWindowing_clause(self, ctx:FirebirdParser.Windowing_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#windowing_type.
    def visitWindowing_type(self, ctx:FirebirdParser.Windowing_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#windowing_elements.
    def visitWindowing_elements(self, ctx:FirebirdParser.Windowing_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#using_clause.
    def visitUsing_clause(self, ctx:FirebirdParser.Using_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#using_element.
    def visitUsing_element(self, ctx:FirebirdParser.Using_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#assignable_element.
    def visitAssignable_element(self, ctx:FirebirdParser.Assignable_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#collect_order_by_part.
    def visitCollect_order_by_part(self, ctx:FirebirdParser.Collect_order_by_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#within_or_over_part.
    def visitWithin_or_over_part(self, ctx:FirebirdParser.Within_or_over_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#string_delimiter.
    def visitString_delimiter(self, ctx:FirebirdParser.String_delimiterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#cost_matrix_clause.
    def visitCost_matrix_clause(self, ctx:FirebirdParser.Cost_matrix_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xml_passing_clause.
    def visitXml_passing_clause(self, ctx:FirebirdParser.Xml_passing_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xml_attributes_clause.
    def visitXml_attributes_clause(self, ctx:FirebirdParser.Xml_attributes_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xml_namespaces_clause.
    def visitXml_namespaces_clause(self, ctx:FirebirdParser.Xml_namespaces_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xml_table_column.
    def visitXml_table_column(self, ctx:FirebirdParser.Xml_table_columnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xml_general_default_part.
    def visitXml_general_default_part(self, ctx:FirebirdParser.Xml_general_default_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xml_multiuse_expression_element.
    def visitXml_multiuse_expression_element(self, ctx:FirebirdParser.Xml_multiuse_expression_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xmlroot_param_version_part.
    def visitXmlroot_param_version_part(self, ctx:FirebirdParser.Xmlroot_param_version_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xmlroot_param_standalone_part.
    def visitXmlroot_param_standalone_part(self, ctx:FirebirdParser.Xmlroot_param_standalone_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xmlserialize_param_enconding_part.
    def visitXmlserialize_param_enconding_part(self, ctx:FirebirdParser.Xmlserialize_param_enconding_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xmlserialize_param_version_part.
    def visitXmlserialize_param_version_part(self, ctx:FirebirdParser.Xmlserialize_param_version_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xmlserialize_param_ident_part.
    def visitXmlserialize_param_ident_part(self, ctx:FirebirdParser.Xmlserialize_param_ident_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#annotations_clause.
    def visitAnnotations_clause(self, ctx:FirebirdParser.Annotations_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#annotations_list.
    def visitAnnotations_list(self, ctx:FirebirdParser.Annotations_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#annotation.
    def visitAnnotation(self, ctx:FirebirdParser.AnnotationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#sql_plus_command.
    def visitSql_plus_command(self, ctx:FirebirdParser.Sql_plus_commandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#start_command.
    def visitStart_command(self, ctx:FirebirdParser.Start_commandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#sql_plus_filepath.
    def visitSql_plus_filepath(self, ctx:FirebirdParser.Sql_plus_filepathContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#whenever_command.
    def visitWhenever_command(self, ctx:FirebirdParser.Whenever_commandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#set_command.
    def visitSet_command(self, ctx:FirebirdParser.Set_commandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#timing_command.
    def visitTiming_command(self, ctx:FirebirdParser.Timing_commandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#clear_command.
    def visitClear_command(self, ctx:FirebirdParser.Clear_commandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#partition_extension_clause.
    def visitPartition_extension_clause(self, ctx:FirebirdParser.Partition_extension_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#column_alias.
    def visitColumn_alias(self, ctx:FirebirdParser.Column_aliasContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#table_alias.
    def visitTable_alias(self, ctx:FirebirdParser.Table_aliasContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#where_clause.
    def visitWhere_clause(self, ctx:FirebirdParser.Where_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#into_clause.
    def visitInto_clause(self, ctx:FirebirdParser.Into_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xml_column_name.
    def visitXml_column_name(self, ctx:FirebirdParser.Xml_column_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#cost_class_name.
    def visitCost_class_name(self, ctx:FirebirdParser.Cost_class_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#attribute_name.
    def visitAttribute_name(self, ctx:FirebirdParser.Attribute_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#savepoint_name.
    def visitSavepoint_name(self, ctx:FirebirdParser.Savepoint_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#rollback_segment_name.
    def visitRollback_segment_name(self, ctx:FirebirdParser.Rollback_segment_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#schema_name.
    def visitSchema_name(self, ctx:FirebirdParser.Schema_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#routine_name.
    def visitRoutine_name(self, ctx:FirebirdParser.Routine_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#package_name.
    def visitPackage_name(self, ctx:FirebirdParser.Package_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#implementation_type_name.
    def visitImplementation_type_name(self, ctx:FirebirdParser.Implementation_type_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#parameter_name.
    def visitParameter_name(self, ctx:FirebirdParser.Parameter_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#reference_model_name.
    def visitReference_model_name(self, ctx:FirebirdParser.Reference_model_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#main_model_name.
    def visitMain_model_name(self, ctx:FirebirdParser.Main_model_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#container_tableview_name.
    def visitContainer_tableview_name(self, ctx:FirebirdParser.Container_tableview_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#aggregate_function_name.
    def visitAggregate_function_name(self, ctx:FirebirdParser.Aggregate_function_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#query_name.
    def visitQuery_name(self, ctx:FirebirdParser.Query_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#grantee_name.
    def visitGrantee_name(self, ctx:FirebirdParser.Grantee_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#role_name.
    def visitRole_name(self, ctx:FirebirdParser.Role_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#constraint_name.
    def visitConstraint_name(self, ctx:FirebirdParser.Constraint_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#label_name.
    def visitLabel_name(self, ctx:FirebirdParser.Label_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#type_name.
    def visitType_name(self, ctx:FirebirdParser.Type_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#sequence_name.
    def visitSequence_name(self, ctx:FirebirdParser.Sequence_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#exception_name.
    def visitException_name(self, ctx:FirebirdParser.Exception_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#function_name.
    def visitFunction_name(self, ctx:FirebirdParser.Function_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#procedure_name.
    def visitProcedure_name(self, ctx:FirebirdParser.Procedure_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#trigger_name.
    def visitTrigger_name(self, ctx:FirebirdParser.Trigger_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#variable_name.
    def visitVariable_name(self, ctx:FirebirdParser.Variable_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#index_name.
    def visitIndex_name(self, ctx:FirebirdParser.Index_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#cursor_name.
    def visitCursor_name(self, ctx:FirebirdParser.Cursor_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#record_name.
    def visitRecord_name(self, ctx:FirebirdParser.Record_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#link_name.
    def visitLink_name(self, ctx:FirebirdParser.Link_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#local_link_name.
    def visitLocal_link_name(self, ctx:FirebirdParser.Local_link_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#connection_qualifier.
    def visitConnection_qualifier(self, ctx:FirebirdParser.Connection_qualifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#column_name.
    def visitColumn_name(self, ctx:FirebirdParser.Column_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#tableview_name.
    def visitTableview_name(self, ctx:FirebirdParser.Tableview_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#xmltable.
    def visitXmltable(self, ctx:FirebirdParser.XmltableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#char_set_name.
    def visitChar_set_name(self, ctx:FirebirdParser.Char_set_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#synonym_name.
    def visitSynonym_name(self, ctx:FirebirdParser.Synonym_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#schema_object_name.
    def visitSchema_object_name(self, ctx:FirebirdParser.Schema_object_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#dir_object_name.
    def visitDir_object_name(self, ctx:FirebirdParser.Dir_object_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#user_object_name.
    def visitUser_object_name(self, ctx:FirebirdParser.User_object_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#grant_object_name.
    def visitGrant_object_name(self, ctx:FirebirdParser.Grant_object_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#column_list.
    def visitColumn_list(self, ctx:FirebirdParser.Column_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#paren_column_list.
    def visitParen_column_list(self, ctx:FirebirdParser.Paren_column_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#keep_clause.
    def visitKeep_clause(self, ctx:FirebirdParser.Keep_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#function_argument.
    def visitFunction_argument(self, ctx:FirebirdParser.Function_argumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#function_argument_analytic.
    def visitFunction_argument_analytic(self, ctx:FirebirdParser.Function_argument_analyticContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#function_argument_modeling.
    def visitFunction_argument_modeling(self, ctx:FirebirdParser.Function_argument_modelingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#respect_or_ignore_nulls.
    def visitRespect_or_ignore_nulls(self, ctx:FirebirdParser.Respect_or_ignore_nullsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#argument.
    def visitArgument(self, ctx:FirebirdParser.ArgumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#type_spec.
    def visitType_spec(self, ctx:FirebirdParser.Type_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#datatype.
    def visitDatatype(self, ctx:FirebirdParser.DatatypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#precision_part.
    def visitPrecision_part(self, ctx:FirebirdParser.Precision_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#native_datatype_element.
    def visitNative_datatype_element(self, ctx:FirebirdParser.Native_datatype_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#bind_variable.
    def visitBind_variable(self, ctx:FirebirdParser.Bind_variableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#general_element.
    def visitGeneral_element(self, ctx:FirebirdParser.General_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#general_element_part.
    def visitGeneral_element_part(self, ctx:FirebirdParser.General_element_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#table_element.
    def visitTable_element(self, ctx:FirebirdParser.Table_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#object_privilege.
    def visitObject_privilege(self, ctx:FirebirdParser.Object_privilegeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#system_privilege.
    def visitSystem_privilege(self, ctx:FirebirdParser.System_privilegeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#constant.
    def visitConstant(self, ctx:FirebirdParser.ConstantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#numeric.
    def visitNumeric(self, ctx:FirebirdParser.NumericContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#numeric_negative.
    def visitNumeric_negative(self, ctx:FirebirdParser.Numeric_negativeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#quoted_string.
    def visitQuoted_string(self, ctx:FirebirdParser.Quoted_stringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#identifier.
    def visitIdentifier(self, ctx:FirebirdParser.IdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#id_expression.
    def visitId_expression(self, ctx:FirebirdParser.Id_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#inquiry_directive.
    def visitInquiry_directive(self, ctx:FirebirdParser.Inquiry_directiveContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#outer_join_sign.
    def visitOuter_join_sign(self, ctx:FirebirdParser.Outer_join_signContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#regular_id.
    def visitRegular_id(self, ctx:FirebirdParser.Regular_idContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#non_reserved_keywords_in_18c.
    def visitNon_reserved_keywords_in_18c(self, ctx:FirebirdParser.Non_reserved_keywords_in_18cContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#non_reserved_keywords_in_12c.
    def visitNon_reserved_keywords_in_12c(self, ctx:FirebirdParser.Non_reserved_keywords_in_12cContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by FirebirdParser#non_reserved_keywords_pre12c.
    def visitNon_reserved_keywords_pre12c(self, ctx:FirebirdParser.Non_reserved_keywords_pre12cContext):
        return self.visitChildren(ctx)



del FirebirdParser