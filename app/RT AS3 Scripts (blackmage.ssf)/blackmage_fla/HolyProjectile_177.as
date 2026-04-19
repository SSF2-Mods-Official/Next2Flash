// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.HolyProjectile_177

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class HolyProjectile_177 extends MovieClip 
    {

        internal var attackBox:MovieClip;
        internal var attackBox2:MovieClip;
        internal var attackBox3:MovieClip;
        internal var self:*;
        internal var character:*;
        internal var temp:*;

        public function HolyProjectile_177()
        {
            addFrameScript(0, this.frame1, 14, this.frame15, 44, this.frame45, 54, this.frame55);
        }

        public function pullInCharacters():void
        {
            var _local_1:Number = NaN;
            var _local_2:Number = NaN;
            this.temp = this.character.getGlobalVariable("fsTargets");
            var _local_3:int;
            while (_local_3 < this.temp.length)
            {
                if (!this.temp[_local_3].isDisposed())
                {
                    _local_1 = ((this.self.getX() - this.temp[_local_3].getX()) / 8);
                    _local_2 = (((this.self.getY() - 100) - this.temp[_local_3].getY()) / 8);
                    this.temp[_local_3].safeMove(_local_1, 0);
                    this.temp[_local_3].safeMove(0, _local_2);
                };
                _local_3++;
            };
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:*;
            var _local_5:*;
            var _local_6:*;
            var _local_7:Number = NaN;
            var _local_8:Number = NaN;
            this.self = SSF2API.getProjectile(this);
            if (((SSF2API.isReady()) && (this.self)))
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
}//package blackmage_fla

