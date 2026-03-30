package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class HolyProjectile_177 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var self:*;
        public var character:*;
        public var temp:*;

        public function HolyProjectile_177()
        {
            super();
            addFrameScript(0, this.frame1, 14, this.frame15, 44, this.frame45, 54, this.frame55);
        }

        public function pullInCharacters():void
        {
            var _local_2:Number = NaN;
            var _local_3:Number = NaN;
            this.temp = this.character.getGlobalVariable("fsTargets");
            for (var _local_1:int = 0; _local_1 < this.temp.length; _local_1++)
            {
                if (this.temp[_local_1].isDisposed())
                {
                    continue;
                };
                _local_2 = ((this.self.getX() - this.temp[_local_1].getX()) / 8);
                _local_3 = (((this.self.getY() - 100) - this.temp[_local_1].getY()) / 8);
                this.temp[_local_1].safeMove(_local_2, 0);
                this.temp[_local_1].safeMove(0, _local_3);
            };
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            if (SSF2API.isReady() && this.self)
            {
                this.character = this.self.getOwner();
                this.self.addToCamera();
                this.self.updateAttackStats({"refreshRate":1});
                this.self.playSound("magic_screech");
                this.self.createTimer(1, 0, this.pullInCharacters);
            };
        }

        internal function frame15():*
        {
            this.self.updateAttackStats({"refreshRate":2});
            this.self.updateAttackBoxStats(1, {
                "damage":2,
                "hitStun":0,
                "direction":140,
                "canDI":false,
                "power":140,
                "kbConstant":40,
                "effectSound":"brawl_magic_s",
                "effect_id":"effect_magichit_light"
            });
        }

        internal function frame45():*
        {
            this.self.destroyTimer(this.pullInCharacters);
        }

        internal function frame55():*
        {
            this.self.removeFromCamera();
            this.self.destroy();
        }


    }
}

