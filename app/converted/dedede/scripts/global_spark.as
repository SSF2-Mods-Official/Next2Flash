package
{
    import flash.display.MovieClip;

    public dynamic class global_spark extends MovieClip
    {

        public function global_spark()
        {
            super();
            addFrameScript(4, this.frame5, 5, this.frame6);
        }

        internal function frame5():*
        {
            stop();
            parent.removeChild(this);
        }

        internal function frame6():*
        {
            gotoAndStop("end");
        }


    }
}

