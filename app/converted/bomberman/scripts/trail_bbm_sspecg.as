package
{
    import flash.display.MovieClip;

    public dynamic class trail_bbm_sspecg extends MovieClip
    {

        public function trail_bbm_sspecg()
        {
            super();
            addFrameScript(6, this.frame7);
        }

        internal function frame7():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

