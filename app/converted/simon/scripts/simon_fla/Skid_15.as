package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class Skid_15 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function Skid_15()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
        }

        internal function frame6():*
        {
            this.self.endAttack();
        }


    }
}

