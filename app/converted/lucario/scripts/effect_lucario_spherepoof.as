package
{
    import flash.display.MovieClip;

    public dynamic class effect_lucario_spherepoof extends MovieClip
    {

        public function effect_lucario_spherepoof()
        {
            super();
            addFrameScript(6, this.frame7);
        }

        internal function frame7():*
        {
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

