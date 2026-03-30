package
{
    import flash.display.MovieClip;

    public dynamic class effect_aurahit_light extends MovieClip
    {

        public function effect_aurahit_light()
        {
            super();
            addFrameScript(12, this.frame13);
        }

        internal function frame13():*
        {
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

