package
{
    import flash.display.MovieClip;

    public dynamic class trail_cfalcon_rjab extends MovieClip
    {

        public function trail_cfalcon_rjab()
        {
            super();
            addFrameScript(15, this.frame16);
        }

        internal function frame16():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

