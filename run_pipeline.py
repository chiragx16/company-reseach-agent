from pipeline import CompanyAuditPipeline

if __name__ == "__main__":
    print("\n" + "="*100)
    print(" COMPANY AUDIT PIPELINE - 4 STAGE ORCHESTRATION ".center(100, "="))
    print("="*100)
    
    # CUSTOMIZE THIS - Change company name as needed
    COMPANY_NAME = "Open AI"
    
    try:
        # Initialize pipeline
        pipeline = CompanyAuditPipeline(company_name=COMPANY_NAME)
        
        # Run all 4 stages
        input("\nPress ENTER to start the pipeline... ")
        success = pipeline.run_full_pipeline()
        
        if success:
            # Show results summary
            pipeline.print_summary()
            
            # Save to file
            print("\nSaving results to file...")
            results_file = pipeline.save_results()
            
            if results_file:
                print(f"\n Complete! Check '{results_file}' for full results.")
            else:
                print(f"\n!! Failed to save results. Check the errors above.")
        else:
            print("\n!! Pipeline execution failed. Check the errors above.")
    
    except KeyboardInterrupt:
        print("\n\n Pipeline interrupted by user.")
    except Exception as e:
        print(f"\n!! Unexpected error: {e}")
        import traceback
        traceback.print_exc()
