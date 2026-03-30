package
{
    import flash.display.MovieClip;

    public dynamic class effect_jump extends MovieClip
    {

        public function effect_jump()
        {
            super();
            addFrameScript(5, this.frame6);
        }

        internal function frame6():*
        {
            stop();
            if ((root != null) && (parent != null))
            {
                parent.removeChild(this);
            };
        }


    }
}

