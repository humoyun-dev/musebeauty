/** @type {import('next').NextConfig} */
const nextConfig = {
  // Statik eksport — nginx beradi (Node serveri yo'q, RAM tejaladi).
  output: "export",
  // Statik eksportда Next rasm optimizatsiyasi ishlamaydi — o'chiramiz.
  images: { unoptimized: true },
  // /catalog → /catalog/index.html (nginx try_files bilan mos)
  trailingSlash: true,
};

export default nextConfig;
