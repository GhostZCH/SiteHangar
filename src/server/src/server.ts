import app from './app';

const PORT = process.env.PORT || 3000;

// 启动服务器
app.listen(PORT, () => {
  console.log('========================================');
  console.log('🚀 kc-v2 server listening on port', PORT);
  console.log('========================================');
});
