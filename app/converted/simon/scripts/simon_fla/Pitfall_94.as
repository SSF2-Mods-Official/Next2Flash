package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class Pitfall_94 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function Pitfall_94()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
        }


    }
}

