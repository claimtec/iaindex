import { redirect } from 'next/navigation';

export default function HomePage() {
  // In production, check authentication here
  // For now, redirect to login
  redirect('/login');
}
