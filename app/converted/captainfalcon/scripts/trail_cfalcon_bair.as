package
{
    import flash.display.MovieClip;

    public dynamic class trail_cfalcon_bair extends MovieClip
    {

        public function trail_cfalcon_bair()
        {
            super();
            addFrameScript(3, this.frame4);
        }

        internal function frame4():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

