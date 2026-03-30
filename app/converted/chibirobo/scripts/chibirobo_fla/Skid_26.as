package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class Skid_26 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function Skid_26()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
        }

        internal function frame8():*
        {
            this.self.endAttack();
        }


    }
}

