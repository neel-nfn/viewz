import * as demo from '../mock/pipelineMock';
import * as basix from './providerBasix';

const source = (import.meta.env.VITE_DATA_SOURCE || 'basix').toLowerCase();

export function getProvider(){
  return source === 'demo' ? demo : basix;
}

export function getSourceLabel(){
  return source === 'demo' ? 'demo' : 'basix';
}

