package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class dust_mc_178 extends MovieClip
    {

        public function dust_mc_178()
        {
            super();
            addFrameScript(10, this.frame11);
        }

        internal function frame11():*
        {
            if ((root != null) && (parent != null))
            {
                parent.removeChild(this);
            };
        }


    }
}

