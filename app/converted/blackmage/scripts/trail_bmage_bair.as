package
{
    import flash.display.MovieClip;

    public dynamic class trail_bmage_bair extends MovieClip
    {

        public function trail_bmage_bair()
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

