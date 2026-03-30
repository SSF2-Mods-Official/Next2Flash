package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class item_shoot_88 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function item_shoot_88()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 15, this.frame16);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
        }

        internal function frame4():*
        {
            this.self.getItem().activateItem();
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-10)});
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }


    }
}

