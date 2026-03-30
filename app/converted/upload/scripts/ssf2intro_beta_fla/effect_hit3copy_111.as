package ssf2intro_beta_fla
{
    import flash.display.MovieClip;

    public dynamic class effect_hit3copy_111 extends MovieClip
    {

        public function effect_hit3copy_111()
        {
            super();
            addFrameScript(7, this.frame8);
        }

        internal function frame8():*
        {
            stop();
            if ((root != null) && (parent != null))
            {
                parent.removeChild(this);
            };
        }


    }
}

