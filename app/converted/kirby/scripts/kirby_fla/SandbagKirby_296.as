package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class SandbagKirby_296 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function SandbagKirby_296()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 3, this.frame4, 12, this.frame13, 21, this.frame22, 29, this.frame30, 33, this.frame34, 39, this.frame40);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
        }

        internal function frame2():*
        {
            this.self.playSound("magic_screech");
        }

        internal function frame4():*
        {
            this.self.attachEffect("Kirby_sandbag_red", {
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true
            });
        }

        internal function frame13():*
        {
            this.self.attachEffect("Kirby_sandbag_green", {
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true
            });
        }

        internal function frame22():*
        {
            this.self.attachEffect("Kirby_sandbag_blue", {
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true
            });
        }

        internal function frame30():*
        {
            if (!this.self.getItem())
            {
                this.self.generateItem("capsule", true, false, true);
                this.self.playSound("sandbag_itemSpawn");
                this.self.attachEffect("sandbag_confetti", {
                    "y":-15,
                    "parentLock":false
                });
                this.self.updateAttackStats({"air_ease":0});
                this.self.resetMovement();
            }
            else
            {
                this.self.endAttack();
            };
        }

        internal function frame34():*
        {
            this.self.updateAttackStats({"air_ease":-1});
        }

        internal function frame40():*
        {
            this.self.endAttack();
        }


    }
}

