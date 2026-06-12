import{i as e}from"./preload-helper-xPQekRTU.js";import{t}from"./iframe-D6ENcTTt.js";import{t as n}from"./jsx-runtime-BNO8td4Y.js";var r,i,a=e((()=>{t(),r=n(),i=({children:e,type:t=`info`})=>{let n={padding:`var(--spacing-md)`,borderRadius:`var(--radius-sm)`,marginBottom:`var(--spacing-md)`,fontSize:`var(--font-size-sm)`,color:`var(--color-text-inverse)`};return t===`info`?n.backgroundColor=`var(--color-blue-600)`:t===`warning`?n.backgroundColor=`var(--color-purple-600)`:t===`error`&&(n.backgroundColor=`var(--color-gray-700)`),(0,r.jsx)(`div`,{style:n,children:e})},i.__docgenInfo={description:``,methods:[],displayName:`Alert`,props:{children:{required:!0,tsType:{name:`ReactReactNode`,raw:`React.ReactNode`},description:``},type:{required:!1,tsType:{name:`union`,raw:`'info' | 'warning' | 'error'`,elements:[{name:`literal`,value:`'info'`},{name:`literal`,value:`'warning'`},{name:`literal`,value:`'error'`}]},description:``,defaultValue:{value:`'info'`,computed:!1}}}}})),o,s,c,l,u;e((()=>{a(),o={title:`UI/Alert`,component:i,parameters:{layout:`centered`},tags:[`autodocs`],argTypes:{type:{control:`select`,options:[`info`,`warning`,`error`]}}},s={args:{type:`info`,children:`This is an informational alert message.`}},c={args:{type:`warning`,children:`Warning: Something might be wrong here.`}},l={args:{type:`error`,children:`Error: Action failed. Please try again.`}},s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
  args: {
    type: 'info',
    children: 'This is an informational alert message.'
  }
}`,...s.parameters?.docs?.source}}},c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    type: 'warning',
    children: 'Warning: Something might be wrong here.'
  }
}`,...c.parameters?.docs?.source}}},l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  args: {
    type: 'error',
    children: 'Error: Action failed. Please try again.'
  }
}`,...l.parameters?.docs?.source}}},u=[`Info`,`Warning`,`Error`]}))();export{l as Error,s as Info,c as Warning,u as __namedExportsOrder,o as default};