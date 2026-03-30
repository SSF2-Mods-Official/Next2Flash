package
{
    import flash.display.MovieClip;

    public dynamic class trail_bmage_pummel extends MovieClip
    {

        public function trail_bmage_pummel()
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

