package
{
    import flash.display.MovieClip;

    public dynamic class trail_bbm_sspeca extends MovieClip
    {

        public function trail_bbm_sspeca()
        {
            super();
            addFrameScript(9, this.frame10);
        }

        internal function frame10():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

