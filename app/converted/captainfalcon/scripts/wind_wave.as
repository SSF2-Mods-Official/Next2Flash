package
{
    import flash.display.MovieClip;

    public dynamic class wind_wave extends MovieClip
    {

        public function wind_wave()
        {
            super();
            addFrameScript(6, this.frame7);
        }

        internal function frame7():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

