package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemHeavyShoot_105 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function ItemHeavyShoot_105()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 25, this.frame26);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
        }

        internal function frame4():*
        {
            this.self.getItem().activateItem();
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-7),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame26():*
        {
            this.self.endAttack();
        }


    }
}

