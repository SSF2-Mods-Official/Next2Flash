package
{
    import flash.display.MovieClip;

    public dynamic class effect_explosion extends MovieClip
    {

        public function effect_explosion()
        {
            super();
            addFrameScript(12, this.frame13);
        }

        internal function frame13():*
        {
            stop();
            if (parent != null)
            {
                parent.removeChild(this);
            };
        }


    }
}

