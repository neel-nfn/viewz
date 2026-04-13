export const DEMO_MODE = false;

export const DEMO_ROLE = (localStorage.getItem('viewz_user_role') || localStorage.getItem('viewz_role') || import.meta.env.VITE_DEMO_ROLE || 'manager').toLowerCase();

export const STAGES = ['research','writing','design','editing','scheduled','published','archived'];

export const PRIORITIES = { low:'low', medium:'medium', high:'high' };

export const DENSITY = (localStorage.getItem("viewz_density")||"comfortable");
export const setDensity = (v)=>{ localStorage.setItem("viewz_density", v); };
export const STAGE_COLORS={research:"badge-info",writing:"badge-primary",design:"badge-secondary",editing:"badge-warning",scheduled:"badge-accent",published:"badge-success",archived:"badge-ghost"};
