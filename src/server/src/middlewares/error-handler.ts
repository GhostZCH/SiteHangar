import { Request, Response, NextFunction } from 'express';

export class HttpError extends Error {
  status: number;
  details?: unknown;
  constructor(status: number, message: string, details?: unknown) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

export function errorHandler(err: any, req: Request, res: Response, _next: NextFunction) {
  if (err instanceof HttpError) {
    return res.status(err.status).json({
      error: err.message,
      ...(err.details ? { details: err.details } : {}),
    });
  }
  console.error('[unhandled]', err);
  res.status(500).json({ error: 'INTERNAL_ERROR', message: err?.message || '服务器内部错误' });
}

export function notFound(req: Request, res: Response) {
  res.status(404).json({ error: 'NOT_FOUND', path: req.path });
}
