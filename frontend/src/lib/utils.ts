import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Utility function for merging Tailwind CSS classes.
 * Combines clsx for conditional classes and tailwind-merge
 * to properly handle Tailwind class conflicts.
 *
 * @param inputs - Class values to merge (strings, arrays, objects)
 * @returns Merged class string with conflicts resolved
 *
 * @example
 * cn('px-4 py-2', 'px-6') // Returns 'py-2 px-6'
 * cn('bg-red-500', condition && 'bg-blue-500')
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
