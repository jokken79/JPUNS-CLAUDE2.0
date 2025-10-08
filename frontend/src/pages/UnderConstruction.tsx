import React from 'react';
import { WrenchScrewdriverIcon } from '@heroicons/react/24/outline';

const UnderConstruction: React.FC = () => {
  return (
    <div className="relative overflow-hidden rounded-3xl border border-dashed border-amber-200/60 bg-amber-50/60 p-10 shadow-lg shadow-amber-500/10">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-10 top-4 h-56 w-56 rounded-full bg-amber-200/40 blur-3xl" />
        <div className="absolute bottom-6 right-12 h-40 w-40 rounded-full bg-orange-200/30 blur-2xl" />
      </div>
      <div className="relative flex flex-col items-start gap-4 text-amber-900">
        <div className="inline-flex items-center gap-3 rounded-full bg-white/80 px-4 py-2 text-xs font-semibold uppercase tracking-[0.3em] text-amber-600 shadow-sm shadow-amber-500/20">
          <WrenchScrewdriverIcon className="h-5 w-5" />
          En construcción
        </div>
        <h1 className="text-2xl font-bold text-amber-900 sm:text-3xl">
          Esta sección aún no está lista para los Kanrinin
        </h1>
        <p className="max-w-2xl text-sm text-amber-800/90 sm:text-base">
          El administrador ha deshabilitado temporalmente esta página mientras se realizan ajustes o configuraciones. Si necesitas acceso, por favor contacta con el administrador del sistema.
        </p>
        <div className="mt-6 grid gap-3 text-sm">
          <div className="flex items-center gap-2 text-amber-800/80">
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-white/80 text-amber-500 shadow shadow-amber-500/10">
              1
            </span>
            <span>Revisa nuevamente más tarde para ver las últimas novedades.</span>
          </div>
          <div className="flex items-center gap-2 text-amber-800/80">
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-white/80 text-amber-500 shadow shadow-amber-500/10">
              2
            </span>
            <span>Comunícate con tu administrador si consideras que necesitas acceso inmediato.</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UnderConstruction;
