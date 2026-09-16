export type User = { id:number; email:string; full_name:string; is_admin:boolean; created_at:string }
export type Step = { id?:number; position:number; step_type:'trigger'|'transform'|'http'|'log'|'delay'|'telegram'; name:string; config:Record<string, unknown> }
export type Workflow = { id:number; name:string; description:string; trigger_type:'manual'|'webhook'|'schedule'; active:boolean; webhook_token:string; schedule_minutes:number|null; created_at:string; updated_at:string; steps:Step[] }
export type ExecutionLog = { id:number; step_name:string; level:string; message:string; payload:Record<string,unknown>; created_at:string }
export type Execution = { id:number; workflow_id:number; workflow_name?:string; trigger:string; status:string; duration_ms:number; input_data:Record<string,unknown>; output_data:Record<string,unknown>; error_message:string; started_at:string; finished_at:string|null; logs:ExecutionLog[] }
export type Integration = { provider:string; display_name:string; description:string; category:string; connected:boolean; status_text:string; config_hint:string }
export type Template = { id:string; name:string; category:string; description:string; trigger_type:string; schedule_minutes?:number; steps:Step[] }
