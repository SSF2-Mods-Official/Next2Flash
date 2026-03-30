package
{
    import flash.display.MovieClip;

    public dynamic class global_smash_spark extends MovieClip
    {

        public function global_smash_spark()
        {
            super();
            addFrameScript(4, this.frame5);
        }

        internal function frame5():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

