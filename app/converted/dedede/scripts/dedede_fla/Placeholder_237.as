package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class Placeholder_237 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var self:DededeExt;

        public function Placeholder_237()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
        }


    }
}

