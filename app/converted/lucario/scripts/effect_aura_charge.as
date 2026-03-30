package
{
    import flash.display.MovieClip;

    public dynamic class effect_aura_charge extends MovieClip
    {

        public function effect_aura_charge()
        {
            super();
            addFrameScript(13, this.frame14);
        }

        internal function frame14():*
        {
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

