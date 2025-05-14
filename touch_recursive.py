#!/usr/bin/env python3
import os
import time
import argparse
import sys
from datetime import datetime

def touch_path(path, verbose=True):
    """Touch a file or directory to update its access and modification times."""
    try:
        os.utime(path, None)
        if verbose:
            print(f"Touched: {path}")
        return True
    except Exception as e:
        print(f"Error touching {path}: {e}")
        return False

def get_all_paths(directory, ignore_patterns=None):
    """Recursively get all files and directories in the given directory."""
    all_paths = []
    
    if ignore_patterns is None:
        ignore_patterns = []
    
    for root, dirs, files in os.walk(directory):
        # Skip directories based on ignore patterns
        dirs[:] = [d for d in dirs if not any(pattern in os.path.join(root, d) for pattern in ignore_patterns)]
        
        # Add the current directory
        all_paths.append(root)
        
        # Add all files in the current directory
        for file in files:
            file_path = os.path.join(root, file)
            if not any(pattern in file_path for pattern in ignore_patterns):
                all_paths.append(file_path)
            
    return all_paths

def touch_in_batches(directory, batch_size, delay_seconds, verbose=True, ignore_patterns=None):
    """Touch all files and directories in batches with a delay between batches."""
    # Normalize and resolve the directory path
    directory = os.path.abspath(os.path.expanduser(directory))
    
    # Check for directory existence
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory or cannot be accessed")
        return False
    
    # Get all paths
    all_paths = get_all_paths(directory, ignore_patterns)
    total_paths = len(all_paths)
    
    if total_paths == 0:
        print(f"No files or directories found in {directory}")
        return False
    
    print(f"Found {total_paths} files and directories to touch")
    
    # Process in batches
    batch_count = 0
    success_count = 0
    error_count = 0
    
    try:
        for i in range(0, total_paths, batch_size):
            batch_count += 1
            batch = all_paths[i:i + batch_size]
            
            print(f"\nBatch {batch_count} - Processing {len(batch)} items ({i+1}-{min(i+batch_size, total_paths)} of {total_paths})")
            start_time = time.time()
            
            # Touch each path in the current batch
            for path in batch:
                if touch_path(path, verbose):
                    success_count += 1
                else:
                    error_count += 1
                
            batch_time = time.time() - start_time
            print(f"Batch {batch_count} completed in {batch_time:.2f} seconds")
            
            # If this isn't the last batch, wait for the specified delay
            if i + batch_size < total_paths:
                if verbose:
                    print(f"Waiting {delay_seconds} seconds before next batch...")
                time.sleep(delay_seconds)
        
        print(f"\nTouching complete: {success_count}/{total_paths} files and directories processed successfully")
        if error_count > 0:
            print(f"Errors encountered: {error_count}")
        
        return error_count == 0
    
    except KeyboardInterrupt:
        print("\nProcess interrupted by user!")
        print(f"Progress: {success_count}/{total_paths} files and directories processed")
        return False

def main():
    parser = argparse.ArgumentParser(description='Touch files and directories recursively in batches.')
    parser.add_argument('directory', help='The directory to process recursively')
    parser.add_argument('-b', '--batch-size', type=int, default=10, help='Number of files/directories to touch in each batch')
    parser.add_argument('-n', '--delay', type=int, default=5, help='Delay in seconds between batches')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output (prints each touched file)')
    parser.add_argument('-i', '--ignore', action='append', default=[], help='Patterns to ignore (can be used multiple times)')
    
    args = parser.parse_args()
    
    print(f"Starting recursive touch at {datetime.now()}")
    print(f"Directory: {os.path.abspath(os.path.expanduser(args.directory))}")
    print(f"Batch size: {args.batch_size}")
    print(f"Delay between batches: {args.delay} seconds")
    
    if args.ignore:
        print(f"Ignoring patterns: {', '.join(args.ignore)}")
    
    # Start touching files
    success = touch_in_batches(
        args.directory, 
        args.batch_size, 
        args.delay, 
        verbose=args.verbose,
        ignore_patterns=args.ignore
    )
    
    print(f"Finished at {datetime.now()}")
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 