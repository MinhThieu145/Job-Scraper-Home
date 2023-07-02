# import indeed scraper
import scraper

# import analyze data function
import job_description_analyzer

# some other libraries
import os
import pandas as pd

# main function
def main():

    # clean the result folder
    # get current dir
    current_dir = os.getcwd()

    # get the result folder if exit
    try:
        # if the result folder exists
        result_dir = os.path.join(current_dir, 'result')
        # delete all the files in the result folder
        for file in os.listdir(result_dir):
            os.remove(os.path.join(result_dir, file))

        
    except:
        # create a new folder called result
        os.mkdir('result')
        result_dir = os.path.join(current_dir, 'result')


    # run the scraper
    scraper.main()

    # get the result from a folder called result

    # loop through the result folder
    for file in os.listdir(result_dir):
        # if that is a csv file
        if file.endswith('.csv'):
            # read with pandas
            df = pd.read_csv(os.path.join(result_dir, file))

            # if the dataframe is not empty
            if not df.empty:
                # pass that to the analyze data function
                job_description_analyzer.main(df=df, df_name=file.split('.')[0])
                    


if __name__ == "__main__":
    main()
