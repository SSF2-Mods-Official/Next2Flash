package
{
    import flash.display.MovieClip;

    public dynamic class trail_bbm_uair extends MovieClip
    {

        public function trail_bbm_uair()
        {
            super();
            addFrameScript(5, this.frame6);
        }

        internal function frame6():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

